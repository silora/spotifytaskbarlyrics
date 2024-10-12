import logging
import sys
import time
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QGraphicsDropShadowEffect, QDesktopWidget
from PyQt5.QtGui import QColor
from PyQt5.QtCore import QTimer, QTime
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QObject, QMutex
from globalvariables import SP_DC
from label import OutlinedLabel
from lyricmanager import FromSpotify, FromThirdParty, LyricsManager
from nowplaying import NowPlayingMixed

class LyricsMaintainer():
    def __init__(self):
        super().__init__()
        self.now_playing = NowPlayingMixed(update_callback=self.update_lyrics)
        self.manager = LyricsManager(providers=[FromSpotify(SP_DC), FromThirdParty()])
        
        self.lyrics = None
        self.updateMutex = QMutex()
        self.now_playing.start_loop()
    
    @property
    def line(self):
        # print(self.now_playing.__dict__)
        if not self.now_playing.has_lyrics:
            return ""
        if not self.now_playing.current_begin_time:
            return ""
        if not self.lyrics:
            return ""
        if not self.now_playing.is_playing:
            return ""
        # add delay
        l = self.lyrics.get_line_with_timestamp(int(time.time()*1000) - self.now_playing.current_begin_time + 600)
        if l:
            # print(l)
            return l
        return ""
    
    def update_lyrics(self, playing_info=None):
        logging.info(self.now_playing.playing_info)
        if not self.updateMutex.tryLock(timeout=0):
            logging.info("UPDATING SKIPPED")
            return
        if not self.now_playing.playing_info:
            self.updateMutex.unlock()
            return
        if not self.now_playing.has_lyrics:
            self.lyrics = None
            self.updateMutex.unlock()
            return
        if not self.now_playing.is_playing:
            logging.info("NOT PLAYING")
            # self.lyrics = None
            self.updateMutex.unlock()
            return
        # if not self.now_playing.current_track_id or not self.now_playing.current_begin_time:
        #     self.updateMutex.unlock()
        #     return
        # if self.current_track_length < int(time.time()*1000) - self.current_begin_time:
        #     logging.info("NEXT TRACK")
        #     self.updateMutex.unlock()
        #     return
        logging.info("GETTING LYRICS")
        self.lyrics = None
        self.manager.get_lyrics(self.now_playing.current_track, lambda x: self.set_lyrics(x))
        print("UPDATED LYRICS: ", self.now_playing.current_track)
        # if not self.lyrics:
        #     logging.info("LYRICS NOT FOUND")
        #     self.now_playing.has_lyrics = False
        # self.updateMutex.unlock()
    
    def set_lyrics(self, value):
        self.lyrics = value
        print("Got Lyrics For", value.lines[0])
        if not self.lyrics:
            logging.info("LYRICS NOT FOUND")
            self.now_playing.has_lyrics = False
        else:
            self.now_playing.has_lyrics = True
        self.updateMutex.unlock()
        
        print("SET LYRICS: ", self.now_playing.current_track)
        
if __name__ == '__main__':
    app = QApplication(sys.argv)
    lm = LyricsMaintainer()
    breakpoint()
    sys.exit(app.exec_())