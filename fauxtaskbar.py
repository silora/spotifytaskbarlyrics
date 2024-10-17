from PyQt5.QtGui import QColor, QImage, QPainter
from PyQt5.QtWidgets import QLabel
import pyautogui
from PIL import Image

def sample_colors_from_geometry(geom):
    width, height = geom.width(), geom.height()
    points = [
        (geom.left(), geom.top()),
        (geom.left() + width, geom.top()),
        (geom.left(), geom.top() + height - 1),
        (geom.left() + width, geom.top() + height - 1),
        (geom.left(), geom.top() + height // 2),
        (geom.left() + width, geom.top() + height // 2)
    ]
    colors = []
    for point in points:
        screenshot = pyautogui.screenshot(region=(point[0], point[1], 1, 1))
        color = Image.frombytes('RGB', screenshot.size, screenshot.tobytes()).getpixel((0, 0))
        colors.append('#{:02x}{:02x}{:02x}'.format(color[0], color[1], color[2]))
    return colors


class FauxTaskbar(QLabel):
    def __init__(self, parent=None, geometry_reference=None):
        super().__init__("", parent)
        self._blending = None
        self.geometry_reference = geometry_reference

    def interpolate_color(self, color1, color2, factor):
        r = color1.red() + (color2.red() - color1.red()) * factor
        g = color1.green() + (color2.green() - color1.green()) * factor
        b = color1.blue() + (color2.blue() - color1.blue()) * factor
        return QColor(int(r), int(g), int(b))

    def mix_colors(self, width, height, x, y, c1, c2, c3, c4, e_left, e_right):
        factor_x = x / width
        factor_y = y / height

        left_color = self.interpolate_color(c1, c3, factor_y)
        right_color = self.interpolate_color(c2, c4, factor_y)

        mid_left = self.interpolate_color(e_left, left_color, factor_y)
        mid_right = self.interpolate_color(e_right, right_color, factor_y)

        final_color = self.interpolate_color(mid_left, mid_right, factor_x)

        return final_color
    
    @property
    def blending(self):
        if self._blending is None:
            width = self.width()
            height = self.height()

            self._blending = QImage(width, height, QImage.Format_RGB32)
            geom = self.geometry_reference.geometry().adjusted(-1, 0, 1, 0)
            colors = [QColor(_) for _ in sample_colors_from_geometry(geom)]
            for x in range(width):
                for y in range(height):
                    # Get the mixed color for the current pixel
                    mixed_color = self.mix_colors(
                        width, height, x, y,
                        *colors
                    )
                    self._blending.setPixelColor(x, y, mixed_color)
        return self._blending
        
    def clear_blending(self):
        print("repainting taskbar")
        self._blending = None
        

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.drawImage(0, 0, self.blending)

