# ui/components.py

from PyQt6 import QtCore, QtGui, QtWidgets
from config import (ANCHOR_X0, ANCHOR_Y0, ANCHOR_X1, ANCHOR_Y1, SAFESPACE_BORDERS,
                    WINDOW_W, WINDOW_H, MAP_OFFSET_X, MAP_WIDTH, STYLE)

class MapCanvas:
    def __init__(self):
        self.rotation = 0
        self.set_limits_and_scale()

    def set_limits_and_scale(self):
        if self.rotation in [90, 270]:
            # Intercambia límites y escalas, y también el tamaño del canvas
            self.min_x_display = ANCHOR_Y0
            self.max_x_display = ANCHOR_Y1
            self.min_y_display = ANCHOR_X0
            self.max_y_display = ANCHOR_X1
            self.scale_x = WINDOW_H / (self.max_x_display - self.min_x_display)   # <-- OJO aquí
            self.scale_y = MAP_WIDTH / (self.max_y_display - self.min_y_display)  # <-- OJO aquí
        else:
            self.min_x_display = ANCHOR_X0
            self.max_x_display = ANCHOR_X1
            self.min_y_display = ANCHOR_Y0
            self.max_y_display = ANCHOR_Y1
            self.scale_x = MAP_WIDTH / (self.max_x_display - self.min_x_display)
            self.scale_y = WINDOW_H / (self.max_y_display - self.min_y_display)

    def set_rotation(self, rotation):
        self.rotation = rotation % 360
        self.set_limits_and_scale()

    def to_canvas_coords(self, x: float, y: float) -> QtCore.QPointF:
        # Centro del área de dibujo
        cx = (ANCHOR_X0 + ANCHOR_X1) / 2
        cy = (ANCHOR_Y0 + ANCHOR_Y1) / 2

        dx = x - cx
        dy = y - cy

        angle = self.rotation
        if angle == 0:
            rx, ry = dx, dy
        elif angle == 90:
            rx, ry = -dy, dx
        elif angle == 180:
            rx, ry = -dx, -dy
        elif angle == 270:
            rx, ry = dy, -dx
        else:
            rx, ry = dx, dy

        if angle in [90, 270]:
            x_rot = cy + rx
            y_rot = cx + ry
            # Intercambia el origen y el escalado
            px = MAP_OFFSET_X + (x_rot - self.min_x_display) * self.scale_x
            py = WINDOW_H - ((y_rot - self.min_y_display) * self.scale_y)
        else:
            x_rot = cx + rx
            y_rot = cy + ry
            px = MAP_OFFSET_X + (x_rot - self.min_x_display) * self.scale_x
            py = WINDOW_H - ((y_rot - self.min_y_display) * self.scale_y)
        return QtCore.QPointF(px, py)
    
def create_safebox_item(canvas: MapCanvas) -> QtWidgets.QGraphicsRectItem:
    """ Crea el QGraphicsRectItem para la zona de seguridad, respetando la rotación. """
    # Calcula las esquinas transformadas
    top_left = canvas.to_canvas_coords(SAFESPACE_BORDERS["min_x"], SAFESPACE_BORDERS["max_y"])
    bottom_right = canvas.to_canvas_coords(SAFESPACE_BORDERS["max_x"], SAFESPACE_BORDERS["min_y"])
    rect = QtCore.QRectF(top_left, bottom_right).normalized()

    pen = QtGui.QPen(QtGui.QColor(STYLE["safe_zone_pen_color"]), 3)
    brush = QtGui.QBrush(QtGui.QColor(STYLE["safe_zone_brush_color"]))
    brush.setColor(QtGui.QColor(brush.color().red(), brush.color().green(), brush.color().blue(), 120))

    item = QtWidgets.QGraphicsRectItem(rect)
    item.setPen(pen)
    item.setBrush(brush)

    return item

def create_point_item() -> QtWidgets.QGraphicsEllipseItem:
    """ Erstellt das QGraphicsItem für den Tag-Punkt. """
    r = 12  # Radius in Pixel
    ellipse = QtWidgets.QGraphicsEllipseItem(-r, -r, 2 * r, 2 * r)
    color = QtGui.QColor(STYLE["tag_safe_color"])
    ellipse.setBrush(QtGui.QBrush(color))
    ellipse.setPen(QtGui.QPen(color, 2))

    glow = QtWidgets.QGraphicsDropShadowEffect()
    glow.setBlurRadius(25)
    glow.setColor(color)
    glow.setOffset(0, 0)
    ellipse.setGraphicsEffect(glow)

    ellipse.setPos(-100, -100)  # Start außerhalb des sichtbaren Bereichs
    ellipse.setZValue(1) # Sicherstellen, dass der Punkt über dem Raster ist
    return ellipse

def create_sidebar(x_pos, width, y_pos, height) -> QtWidgets.QGraphicsRectItem:
    """Erstellt den Hintergrund für eine Seitenleiste an beliebiger Position."""
    rect = QtCore.QRectF(x_pos, y_pos, width, height)
    bg = QtWidgets.QGraphicsRectItem(rect)
    bg.setBrush(QtGui.QBrush(QtGui.QColor(STYLE["sidebar_bg_color"])))
    bg.setPen(QtGui.QPen(QtGui.QColor(STYLE["sidebar_border_color"]), 2))
    return bg
