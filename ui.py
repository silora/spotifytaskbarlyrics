import sys
import time
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QGraphicsDropShadowEffect, QDesktopWidget, QShortcut, QFrame
from PyQt5.QtGui import QColor, QKeySequence, QMouseEvent, QPalette
from PyQt5.QtCore import QTimer, QTime
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QObject, QMutex
from label import OutlinedLabel
from lyricmanager import FromSpotify, LyricsManager
from globalvariables import SP_DC
from lyricsmaintainer import LyricsMaintainer
        
class LyricsDisplay(QWidget):
    def __init__(self):
        super().__init__()
        self.main_frame = QWidget()
        self.layout = QVBoxLayout()
        self.layout.setSpacing(0)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.main_frame.setStyleSheet("background-color: rgba(0, 0, 0, 0.01)")
        self.main_frame.setFixedSize(QDesktopWidget().screenGeometry().width(), 100)
        self.main_frame.setLayout(self.layout)
        self.main_frame.setAttribute(Qt.WA_TransparentForMouseEvents)
        self.windowConfig()
        self.initUI()
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.updateLyrics)
        self.update_threads = set()
        self.lyric_maintainer = LyricsMaintainer()
        self.timer.start(100) 
        self.setMouseTracking(True)
        
        self.ishidden = False
        self._drag_active = False


    def copyLyricsToClipboard(self):
        clipboard = QApplication.clipboard()
        print("COPYING TO CLIPBOARD")
        clipboard.setText(self.label.text())
        
    def windowConfig(self):
        self.setWindowFlags(self.windowFlags() | Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool | Qt.WindowTransparentForInput)
        # self.setWindowFlags(self.windowFlags()| Qt.WindowStaysOnTopHint | Qt.Tool |  Qt.WindowTransparentForInput) 
        self.setAttribute(Qt.WA_TranslucentBackground)

        ag = QDesktopWidget().availableGeometry()
        sg = QDesktopWidget().screenGeometry()

        print(sg.height())
        self.setFixedSize(sg.width()-1000, 69)
        widget = self.geometry()
        x = (sg.width() - widget.width()) // 2
        y = sg.height() - 69
        self.move(x, y)
        
    def initUI(self):

        self.label = OutlinedLabel("Initializing Lyrics", parent=self.main_frame, linewidth=0, relative_outline=False, brushcolor=QColor(138, 206, 0, 255), linecolor=QColor(255, 255, 255, 100))
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setStyleSheet("font-family: 'Arial Narrow'; font-size: 40px; color: #8ACE00") #;background-color:#222222")
        glow = QGraphicsDropShadowEffect()
        glow.setColor(QColor(138, 206, 0, 255))
        glow.setOffset(0, 0)
        glow.setBlurRadius(7)
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
        self.copyLyricsToClipboard()
        self.previous_pos = e.globalPos()

    def mouseMoveEvent(self, e):
        delta = e.globalPos() - self.previous_pos
        self.move(self.x() + delta.x(), self.y()+delta.y())
        self.previous_pos = e.globalPos()

        self._drag_active = True

    def mouseReleaseEvent(self, e):
        if self._drag_active:
            self._drag_active = False
    
    # def mouseReleaseEvent(self, e):
    #     posMouse =  e.pos()
    #     if self.rect().contains(posMouse):
    #         if not self.ishidden:
    #             self.ishidden = True
    #             self.label.setStyleSheet("background-color:transparent; border: 1px solid black")
    #     else:
    #         if self.ishidden:
    #             self.ishidden = False
    #             self.label.setStyleSheet("font-family: 'Arial Narrow'; font-size: 40px; color: #8ACE00; background-color:white")
    #     return super().mouseReleaseEvent(e)
    
    # def enterEvent(self, e):
    #     if not self.rect().contains(e.pos()):
    #         return
    #     print("Hovering")
    #     if not self.ishidden:
    #         self.ishidden = True
    #         self.label.setHidden(True)
        
    # def leaveEvent(self, e):
    #     # if not self.rect().contains(e.pos()):
    #     #     return
    #     print("Unhovering")
    #     if self.ishidden:
    #         self.ishidden = False
    #         self.label.setHidden(False)
            
    def updateLyrics(self):
        self.raise_()   
        self.label.setText(self.lyric_maintainer.line)
        


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = LyricsDisplay()
    sys.exit(app.exec_())
