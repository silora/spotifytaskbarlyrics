
import sys
import time
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QGraphicsDropShadowEffect, QDesktopWidget
from PyQt5.QtGui import QColor
from PyQt5.QtCore import QTimer, Qt, QThread, pyqtSignal, QObject, QMutex
from label import OutlinedLabel
from lyric_helper import filter_line_with_timestamp, get_info, get_lyrics

class LyricsGrabber(QObject):
    lyrics_ready = pyqtSignal(str)
    def __init__(self, maintainer):
        super().__init__()
        self.maintainer = maintainer

    def getLyrics(self):
        lyric = filter_line_with_timestamp(self.maintainer.all_lyrics, self.maintainer.current_begin_time)
        self.lyrics_ready.emit(lyric)   

class LyricsGrabberThread(QThread):
    def __init__(self, maintainer=None):
        super().__init__()
        self.lyric_grabber = LyricsGrabber(maintainer)
        self.lyric_grabber.moveToThread(self)
        self.started.connect(self.lyric_grabber.getLyrics)
        self.lyric_grabber.lyrics_ready.connect(lambda _ : maintainer.setLyrics(_, update_thread=self))
        self.lyric_grabber.lyrics_ready.connect(self.lyric_grabber.deleteLater)
        self.finished.connect(self.deleteLater)
        

class LyricsMaintainer(QObject):
    def __init__(self):
        super().__init__()
        self.sync_timer = QTimer(self)
        self.sync_timer.timeout.connect(self.syncWithSpotify)
        self.sync_timer.start(15000)
        self.lyric_update_timer = QTimer(self)
        self.lyric_update_timer.timeout.connect(self.updateLyrics)
        self.lyric_update_timer.start(300)
        self.update_threads = set()
        print(">> Timer started")
        
        self.current_track_id = None
        self.current_begin_time = None
        self.current_track_length = None
        self.all_lyrics = {}
        self.lyric = ""
        self.is_playing = False
        
        self.syncMutex = QMutex()
        self.updateMutex = QMutex()
        
        self.syncWithSpotify()
    
    def setLyrics(self, lyrics, update_thread=None):
        update_thread.quit()
        if not update_thread.isFinished():
            update_thread.wait()
        if update_thread in self.update_threads:
            self.update_threads.remove(update_thread)
        self.lyric = lyrics
        print(">> LYRICS UPDATED", lyrics)
    
    def syncWithSpotify(self):
        if not self.syncMutex.tryLock(timeout=0):
            print("]] SYNCING SKIPPED")
            return
        track_id = None
        progress = None
        current_time = None
        is_playing = None
        try:
            print(">> SYNCING")
            track_id, progress, track_length, is_playing = get_info((("item", "id"), ("progress_ms",), ("item", "duration_ms"), ("is_playing",)))
            current_time = int(time.time()*1000)
        except:
            self.syncMutex.unlock()
            return
        if not is_playing:
            self.is_playing = False
            self.syncMutex.unlock()
            return
        current_begin_time = current_time - progress
        if self.current_track_id != track_id or abs(self.current_begin_time - current_begin_time) > 100:
            print(">> NOW PLAYING", track_id)
            self.current_track_id = track_id
            self.current_begin_time = current_begin_time
            self.current_track_length = track_length
            self.all_lyrics = get_lyrics(track_id)
            self.is_playing = True
        self.syncMutex.unlock()
    
    def updateLyrics(self):
        if not self.updateMutex.tryLock(timeout=0):
            print("]] UPDATING SKIPPED")
            return
        if not self.is_playing:
            self.lyric = ""
            self.updateMutex.unlock()
            return
        if not self.current_track_id or not self.current_begin_time:
            self.updateMutex.unlock()
            return
        if self.current_track_length < int(time.time()*1000) - self.current_begin_time:
            print(">> NEXT TRACK")
            self.syncWithSpotify()
            self.updateMutex.unlock()
            return
        print(">> UPDATING LYRICS")
        update_thread = LyricsGrabberThread(self)
        self.update_threads.add(update_thread)
        update_thread.start()
        self.updateMutex.unlock()
            
        
class LyricsDisplay(QWidget):
    def __init__(self):
        super().__init__()
        self.windowConfig()
        self.initUI()
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.updateLyrics)
        self.timer.start(300) 
        self.update_threads = set()
        self.lyric_maintainer = LyricsMaintainer()

    def windowConfig(self):
        self.setWindowFlags(self.windowFlags() | Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool | Qt.WindowTransparentForInput)
        self.setAttribute(Qt.WA_TranslucentBackground)
    
        ## location_on_the_screen
        ag = QDesktopWidget().availableGeometry()
        sg = QDesktopWidget().screenGeometry()

        
        self.setFixedSize(sg.width(), 150)
        widget = self.geometry()
        # x = ag.width() - widget.width()
        y = sg.height() - widget.height() - 70
        self.move(0, y)
        
    def initUI(self):
        self.layout = QVBoxLayout()
        self.label = OutlinedLabel("Initializing Lyrics", parent=self, linewidth=3, relative_outline=False, brushcolor=Qt.red, linecolor=QColor(255, 255, 255, 100))
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setStyleSheet("font-family: 'Motomami'; font-size: 80px; color: red")
        glow = QGraphicsDropShadowEffect()
        glow.setColor(Qt.GlobalColor.red)
        glow.setOffset(0,0)
        glow.setBlurRadius(100)
        self.label.setGraphicsEffect(glow)
        # shadow = QGraphicsDropShadowEffect()
        # shadow.setColor(Qt.GlobalColor.white)
        # shadow.setOffset(0,0)
        # shadow.setBlurRadius(100)
        # self.label.setGraphicsEffect(shadow)
        self.layout.addWidget(self.label)
        self.setLayout(self.layout)
        self.setWindowTitle('Lyrics Display')
        self.show()

    def mousePressEvent(self, e):
        self.previous_pos = e.globalPos()

    def mouseMoveEvent(self, e):
        delta = e.globalPos() - self.previous_pos
        self.move(self.x() + delta.x(), self.y()+delta.y())
        self.previous_pos = e.globalPos()

        self._drag_active = True

    def mouseReleaseEvent(self, e):
        if self._drag_active:
            self._drag_active = False

    def updateLyrics(self):
        self.label.setText(self.lyric_maintainer.lyric)
        


# class LyricsGrabber(QObject):
#     lyrics_ready = pyqtSignal(str)

#     def getLyrics(self):
#         print(">> GRABBING")
#         lyric = current_lyrics()
#         self.lyrics_ready.emit(lyric)   

# class LyricsGrabberThread(QThread):
#     def __init__(self, parent=None, ui=None):
#         super().__init__()
#         self.lyric_grabber = LyricsGrabber()
#         self.lyric_grabber.moveToThread(self)
#         self.started.connect(self.lyric_grabber.getLyrics)
#         self.lyric_grabber.lyrics_ready.connect(lambda _ : ui.setLyrics(_, update_thread=self))
#         self.lyric_grabber.lyrics_ready.connect(self.lyric_grabber.deleteLater)
#         self.finished.connect(self.deleteLater)

# class

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = LyricsDisplay()
    sys.exit(app.exec_())
