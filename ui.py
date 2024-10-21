import sys
import time
import traceback

from pynput.mouse import Controller
from PyQt5.QtCore import (QMutex, QObject, QPropertyAnimation, Qt, QThread,
                          QTime, QTimer, QPoint, pyqtSignal, pyqtProperty, QRect)
from PyQt5.QtGui import QColor, QCursor, QKeySequence, QMouseEvent, QPalette, QPixmap
from PyQt5.QtWidgets import (QApplication, QDesktopWidget, QFrame,
                             QGraphicsDropShadowEffect, QGraphicsOpacityEffect,
                             QLabel, QShortcut, QVBoxLayout, QWidget)

from globalvariables import TAKSBAR_HEIGHT
from label import OutlinedLabel
from lyricmanager import FromSpotify, LyricsManager
from lyricsmaintainer import LyricsMaintainer


from fauxtaskbar import FauxTaskbar, sample_colors_from_geometry
from nowplaying import PlayingStatusTrigger


class LyricsDisplay(QWidget):
    def __init__(self):
        super().__init__()
        self.windowConfig()
        
        self.frame = QFrame(self)
        
        self.faux_taskbar = FauxTaskbar(self.frame, geometry_reference=self)
        self.faux_taskbar.setAlignment(Qt.AlignCenter)
        self.faux_taskbar.setGeometry(0, 0, self.width(), self.height())
        
        self.pad = QLabel("", parent=self.frame)
        self.pad.setAlignment(Qt.AlignCenter)
        self.pad.setGeometry(0, 0, self.width(), self.height())
        
        self.label = OutlinedLabel("", parent=self.frame, linewidth=0, relative_outline=False, brushcolor=QColor(138, 206, 0, 255), linecolor=QColor(255, 255, 255, 100))
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setGeometry(0, 0, self.width(), self.height())
        self.show()
        
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.updateLyrics)
        self.timer.start(100) 
        
        self.setMouseTracking(True)
        
        self.displaying_line = None
        self.lyrics_hidden = False
        self._drag_active = False
        
        self.style_name = None
        self.reappear_timer = QTimer(self)
        self.reappear_timer.setSingleShot(True)
        self.reappear_timer.timeout.connect(self.reappear)
        
        self.entering = None  
        self.sustain = None
        
        self.lyric_maintainer = LyricsMaintainer(self.maintainer_callback)

    def copyLyricsToClipboard(self):
        clipboard = QApplication.clipboard()
        print("COPYING TO CLIPBOARD")
        clipboard.setText(self.label.text())
        
    def windowConfig(self):
        self.setWindowFlags(self.windowFlags() | Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool) # | Qt.WindowTransparentForInput)
        # self.setWindowFlags(self.windowFlags()| Qt.WindowStaysOnTopHint | Qt.Tool) 
        self.setAttribute(Qt.WA_NativeWindow)
        self.setAttribute(Qt.WA_TranslucentBackground)

        ag = QDesktopWidget().availableGeometry()
        sg = QDesktopWidget().screenGeometry()

        
        # print(sg.width(), sg.height())
        self.setFixedSize(sg.width()-1000, TAKSBAR_HEIGHT - 1)
        widget = self.geometry()
        x = (sg.width() - widget.width()) // 2
        y = sg.height() - TAKSBAR_HEIGHT + 1
        self.move(x, y)


    def updateStyle(self):
        style = self.lyric_maintainer.style
        if style["name"] == self.style_name:
            return
        # self.faux_taskbar.clear_blending()
        # self.label.setStyleSheet(f"font-family: '{style['font-family']}'; font-weight: {style['font-weight']}")
        self.label.setBrush(QColor(*style["font-color"]) if isinstance(style["font-color"], tuple) else QColor(style["font-color"]))
        self.label.setPen(QColor(*style["line-color"]) if isinstance(style["line-color"], tuple) else QColor(style["line-color"]))
        self.label.setOutlineThickness(style["line-width"])
        self.label.font_size = int(style['font-size'].replace("px", ""))
        self.label.font_family = style['font-family']
        if style['font-weight'] == "light":
            self.label.font_weight = 25
        elif style['font-weight'] == "normal":
            self.label.font_weight = 50
        elif style['font-weight'] == "demibold":
            self.label.font_weight = 63
        elif style['font-weight'] == "bold":
            self.label.font_weight = 75
        elif style['font-weight'] == "black":
            self.label.font_weight = 87
        self.pad.setStyleSheet(f"background-color: {('rgba' + str(style['background-color'])) if isinstance(style['background-color'], tuple) else style['background-color']}" if style["background-color"] != "transparent" else "")
        if "background-image"  in style:
            image = QPixmap(style["background-image"])
            image = image.scaled(1, self.pad.height(), Qt.KeepAspectRatioByExpanding)
            self.pad.setPixmap(image)
        else:
            self.pad.setPixmap(QPixmap())
        self.label.flip = style["flip-text"]
        self.label.opacity = 1
        self.pad.update()
        self.label.update()
        if style["use-shadow"]:
            glow = QGraphicsDropShadowEffect()
            glow.setColor(QColor(*style["shadow-color"]) if isinstance(style["shadow-color"], tuple) else QColor(style["shadow-color"]))
            glow.setOffset(style["shadow-offset"][0], style["shadow-offset"][1])
            glow.setBlurRadius(style["shadow-radius"])
            self.label.setGraphicsEffect(glow)
        if style["entering"] == "fadein":
            self.entering = QPropertyAnimation(self.label, b"opacity")
            self.entering.setDuration(150)
            self.entering.setStartValue(0.1)
            self.entering.setEndValue(1.0)   
        elif style["entering"] == "zoomin":
            self.entering = QPropertyAnimation(self.label, b"font_size")
            self.entering.setDuration(200)
            self.entering.setStartValue(1)
            self.entering.setEndValue(int(style["font-size"].replace("px", "")))
        elif style["entering"] == "zoomin_overscale":
            self.entering = QPropertyAnimation(self.label, b"font_size")
            self.entering.setDuration(200)
            self.entering.setStartValue(1)
            self.entering.setKeyValueAt(0.7, int(style["font-size"].replace("px", ""))+10)
            self.entering.setEndValue(int(style["font-size"].replace("px", "")))
        else:
            self.entering = None
        # if self.entering is not None:
        #     self.entering.finished.connect(self.sustaining_animation)
        # self.sustain = QPropertyAnimation(self.label, b"geometry")
        # self.sustain.setDuration(1000)
        # self.sustain.setLoopCount(1)
        # base = QRect(self.geometry())
        # self.sustain.setStartValue(base)
        # self.sustain.setKeyValues([(0.1, base.adjust(-1, 2, 0, 0)), (0.4, base.adjust(2, 4, 0, 0)), (0.9, base.adjust(3, 6, 0, 0)), (1, base.adjust(-2, -3, 0, 0))])
        # self.sustain.setEndValue(base)
        self.style_name = style["name"]
        return 
    
    def maintainer_callback(self, value):
        if value == PlayingStatusTrigger.PAUSE:
            print("!!PAUSING")
            self.setHidden(True)
        elif value == PlayingStatusTrigger.RESUME:
            print("!!RESUMING")
            self.setHidden(False)
        elif value == PlayingStatusTrigger.NEW_TRACK:
            print("!!NEW TRACK")
            self.updateStyle()
            self.setHidden(False)
    
    def sustaining_animation(self):
        if self.sustain.state() == QPropertyAnimation.Running:
            return
        print("SUSTAINING")
        self.sustain.start()
    
    def entering_animation(self):
        if self.entering is None:
            return
        if self.sustain is not None and self.sustain.state() == QPropertyAnimation.Running:
            print("STOP SUSTAINING")
            self.sustain.stop()
        if self.entering.state() == QPropertyAnimation.Running:
            self.entering.stop()
        self.entering.start()
        
    def updateLyrics(self, anim=True):
        if self.lyrics_hidden:
            return
        self.raise_()
        text = None
        line = self.lyric_maintainer.line
        # if self.lyric_maintainer.style and self.lyric_maintainer.style != self.style_name:
        #     self.updateStyle()
        if line == self.displaying_line:
            return
        self.displaying_line = line
        text = line.text if line else ""
        text = self.lyric_maintainer.style["format"](text)
        self.label.setText(text)
        if text != "" and anim:
            self.entering_animation()
            
    def setHidden(self, hidden):
        self.lyrics_hidden = hidden
        if hidden:
            self.faux_taskbar.setHidden(True)
            self.pad.setHidden(True)
            self.label.setHidden(True)
        else:
            self.label.setHidden(False)
            self.pad.setHidden(False)
            self.faux_taskbar.setHidden(False)
        

    def reappear(self):
        if self.geometry().contains(QCursor.pos()):
            self.reappear_timer.start(1000)
            return
        self.setHidden(False)
        
    def enterEvent(self, e):
        if self.lyrics_hidden:
            return
        if QApplication.queryKeyboardModifiers() & Qt.ControlModifier == Qt.ControlModifier:
            # self.copyLyricsToClipboard()
            return
        self.lyrics_hidden = True   
        self.setHidden(True)
        self.reappear_timer.start(1000)
        
    def mousePressEvent(self, e):
        if e.button() == Qt.LeftButton:
            self.copyLyricsToClipboard()
        elif e.button() == Qt.RightButton:
            self.lyric_maintainer.next_source()
        elif e.button() == Qt.MiddleButton:
            if QApplication.keyboardModifiers() & Qt.ShiftModifier == Qt.ShiftModifier:
                self.lyric_maintainer.set_empty_lyrics()
            else:
                self.lyric_maintainer.track_offset = 0
        
    # def keyReleaseEvent(self, e):
    #     print("RELEASED")
    #     if e.key() == Qt.Key_Control and self.geometry().contains(QCursor.pos()):
    #         self.enterEvent(None)
            
    def wheelEvent(self, e):
        QModifiers = QApplication.keyboardModifiers()
        if QModifiers & Qt.ShiftModifier == Qt.ShiftModifier:
            print("global", e.angleDelta().y())
            self.lyric_maintainer.global_offset += e.angleDelta().y()
        else:
            print("song", e.angleDelta().y())
            self.lyric_maintainer.track_offset += e.angleDelta().y()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = LyricsDisplay()
    sys.exit(app.exec_())