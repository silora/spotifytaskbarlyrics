import math
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
        
class OutlinedLabel(QLabel):
    
    def __init__(self, text=None, relative_outline=True, linewidth=1/25, brushcolor=Qt.white, linecolor=Qt.black, parent=None, **kwargs):
        super().__init__(text=text, parent=parent, **kwargs)
        self.w = linewidth
        self.mode = relative_outline
        self.setBrush(brushcolor)
        self.setPen(linecolor)
        self.flip = False
        self._opacity = 1
        self._font_size = 1
        self._offset = -1
        
    @pyqtProperty(float)
    def opacity(self):
        return self._opacity
    
    @opacity.setter
    def opacity(self, value):
        self._opacity = value
        self.update()
        
    @pyqtProperty(int)
    def font_size(self):
        return self._font_size
    
    @font_size.setter
    def font_size(self, value):
        self._font_size = value
        self.update()
        
    @pyqtProperty(str)
    def font_family(self):
        return self.font().family()
    
    @font_family.setter
    def font_family(self, value):
        f = self.font()
        f.setFamily(value)
        self.setFont(f)
        
    @pyqtProperty(int)
    def font_weight(self):
        return self.font().weight()
    
    @font_weight.setter
    def font_weight(self, value):
        f = self.font()
        f.setWeight(value)
        self.setFont(f)
        
    def scaledOutlineMode(self):
        return self.mode

    def setScaledOutlineMode(self, state):
        self.mode = state

    def outlineThickness(self):
        return self.w * self.font().pointSize() if self.mode else self.w

    def setOutlineThickness(self, value):
        self.w = value

    def setBrush(self, brush):
        if not isinstance(brush, QBrush):
            brush = QBrush(brush)
        self.brush = brush

    def setPen(self, pen):
        if not isinstance(pen, QPen):
            pen = QPen(pen)
        pen.setJoinStyle(Qt.RoundJoin)
        self.pen = pen

    def sizeHint(self):
        w = math.ceil(self.outlineThickness() * 2)
        return super().sizeHint() + QSize(w, w)
    
    def minimumSizeHint(self):
        w = math.ceil(self.outlineThickness() * 2)
        return super().minimumSizeHint() + QSize(w, w)
    
    def paintEvent(self, event):
        w = self.outlineThickness()
        rect = self.rect()
        metrics = QFontMetrics(self.font())
        if self.font() is not None:
            f = self.font()
            f.setPixelSize(self.font_size)
            self.setFont(f)
        tr = metrics.boundingRect(self.text()).adjusted(0, 0, w, w)
        if self.indent() == -1:
            if self.frameWidth():
                indent = (metrics.boundingRect('x').width() + w * 2) / 2
            else:
                indent = w
        else:
            indent = self.indent()

        if self.alignment() & Qt.AlignLeft:
            x = rect.left() + indent - min(metrics.leftBearing(self.text()[0]), 0)
        elif self.alignment() & Qt.AlignRight:
            x = rect.x() + rect.width() - indent - tr.width()
        else:
            x = (rect.width() - tr.width()) / 2
            
        if self.alignment() & Qt.AlignTop:
            y = rect.top() + indent + metrics.ascent()
        elif self.alignment() & Qt.AlignBottom:
            y = rect.y() + rect.height() - indent - metrics.descent()
        else:
            y = (rect.height() + metrics.ascent() - metrics.descent()) / 2

        path = QPainterPath()
        path.addText(x, y, self.font(), self.text())
        path.setFillRule(Qt.WindingFill)
        path = path.simplified()
        qp = QPainter(self)
        qp.setOpacity(self.opacity)
        qp.setRenderHint(QPainter.Antialiasing)
        
        if self.flip:
            qp.scale(-1, 1)
            qp.translate(-self.width(), 0)

        if self.outlineThickness() > 0:
            self.pen.setWidthF(w * 2)
            qp.strokePath(path, self.pen)
        if 1 < self.brush.style() < 15:
            qp.fillPath(path, self.palette().window())
        qp.fillPath(path, self.brush)