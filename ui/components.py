# ui/components.py

from PyQt6 import QtCore, QtGui, QtWidgets
from config import (ANCHOR_X0, ANCHOR_Y0, ANCHOR_X1, ANCHOR_Y1, SAFESPACE_BORDERS,
                    WINDOW_W, WINDOW_H, MAP_OFFSET_X, MAP_WIDTH, STYLE)

class MapCanvas:
    """ Verwaltet die Umrechnung von realen zu Canvas-Koordinaten. """
    def __init__(self):
        # Berechne den Anzeigebereich mit einem kleinen Rand
        display_margin = 1.0  # Meter
        self.min_x_display = ANCHOR_X0
        self.max_x_display = ANCHOR_X1 + display_margin
        self.min_y_display = ANCHOR_Y0
        self.max_y_display = ANCHOR_Y1 + display_margin
        
        self.scale_x = MAP_WIDTH / (self.max_x_display - self.min_x_display)
        self.scale_y = WINDOW_H / (self.max_y_display - self.min_y_display)

    def to_canvas_coords(self, x: float, y: float) -> QtCore.QPointF:
        """ Wandelt reale Koordinaten (x, y) in Pixel-Koordinaten der Szene um. """
        cx = MAP_OFFSET_X + (x - self.min_x_display) * self.scale_x
        cy = WINDOW_H - ((y - self.min_y_display) * self.scale_y)
        return QtCore.QPointF(cx, cy)

def draw_grid(scene: QtWidgets.QGraphicsScene, canvas: MapCanvas):
    """ Zeichnet das Hintergrundraster auf die Szene. """
    pen = QtGui.QPen(QtGui.QColor(STYLE["grid_color"]), 1, QtCore.Qt.PenStyle.DotLine)
    # Vertikale Linien
    for i in range(int(canvas.max_x_display) + 1):
        x_real = float(i)
        if x_real >= canvas.min_x_display:
            pt = canvas.to_canvas_coords(x_real, canvas.min_y_display)
            scene.addLine(pt.x(), 0, pt.x(), WINDOW_H, pen)
    # Horizontale Linien
    for i in range(int(canvas.max_y_display) + 1):
        y_real = float(i)
        if y_real >= canvas.min_y_display:
            pt = canvas.to_canvas_coords(canvas.min_x_display, y_real)
            scene.addLine(MAP_OFFSET_X, pt.y(), MAP_OFFSET_X + MAP_WIDTH, pt.y(), pen)

def create_safebox_item(canvas: MapCanvas) -> QtWidgets.QGraphicsRectItem:
    """ Erstellt das QGraphicsItem für die Sicherheitszone. """
    top_left = canvas.to_canvas_coords(SAFESPACE_BORDERS["min_x"], SAFESPACE_BORDERS["max_y"])
    bottom_right = canvas.to_canvas_coords(SAFESPACE_BORDERS["max_x"], SAFESPACE_BORDERS["min_y"])
    rect = QtCore.QRectF(top_left, bottom_right)

    pen = QtGui.QPen(QtGui.QColor(STYLE["safe_zone_pen_color"]), 3)
    brush = QtGui.QBrush(QtGui.QColor(STYLE["safe_zone_brush_color"]))
    brush.setColor(QtGui.QColor(brush.color().red(), brush.color().green(), brush.color().blue(), 120))

    item = QtWidgets.QGraphicsRectItem(rect)
    item.setPen(pen)
    item.setBrush(brush)

    glow = QtWidgets.QGraphicsDropShadowEffect()
    glow.setBlurRadius(20)
    glow.setColor(QtGui.QColor(STYLE["safe_zone_glow_color"]))
    glow.setOffset(0, 0)
    item.setGraphicsEffect(glow)
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
