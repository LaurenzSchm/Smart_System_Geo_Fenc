# ui/main_window.py

import time
from PyQt6 import QtCore, QtGui, QtWidgets
from config import WINDOW_W, WINDOW_H, STYLE, LEFT_SIDEBAR_W_RATIO, MAP_WIDTH, TARGET_TAG_ID
from models import Tag, safespace_zone
from .components import MapCanvas, draw_grid, create_safebox_item, create_point_item, create_sidebar

class SafespaceWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()

        self.tag = Tag(TARGET_TAG_ID)
        self.canvas = MapCanvas()
        
        self._setup_ui()
        self._create_layout()

        # Trail-Pfad initialisieren
        self.trail_path = QtGui.QPainterPath()
        self.trail_item = self.scene.addPath(
            self.trail_path,
            QtGui.QPen(QtGui.QColor("#ffff00"), 2)
        )
        self.record_trail = True

        # Timer für Uhrzeit-Update
        self.ui_timer = QtCore.QTimer(self)
        self.ui_timer.timeout.connect(self.update_time)
        self.ui_timer.start(1000)

    def _setup_ui(self):
        self.setWindowTitle("Sci-Fi Safespace Monitor")
        self.setFixedSize(WINDOW_W, WINDOW_H + 20)
        self.scene = QtWidgets.QGraphicsScene(0, 0, WINDOW_W, WINDOW_H)
        self.view = QtWidgets.QGraphicsView(self.scene, self)
        self.view.setRenderHints(
            QtGui.QPainter.RenderHint.Antialiasing |
            QtGui.QPainter.RenderHint.SmoothPixmapTransform
        )
        self.setCentralWidget(self.view)
        self.view.setStyleSheet(f"background-color: {STYLE['background_color']}; border: none;")
        self.status_bar = self.statusBar()
        self.status_bar.setStyleSheet(
            f"background-color: #111; color: {STYLE['primary_text_color']};"
            f"font: 11pt '{STYLE['body_font'][0]}';"
        )
        self.status_bar.showMessage("Warte auf Daten...")

    def _create_layout(self):
        draw_grid(self.scene, self.canvas)
        self.scene.addItem(create_safebox_item(self.canvas))

        self.point_item = create_point_item()
        self.scene.addItem(self.point_item)

        self._create_left_sidebar()

        # Reset-Trail-Button
        btn = QtWidgets.QPushButton("Reset Trail")
        btn.setStyleSheet("background-color: #222; color: #0ff;")
        btn.clicked.connect(self.clear_trail)
        proxy = self.scene.addWidget(btn)
        proxy.setPos(20, 150)

    def _create_text_item(self, text, pos, color=STYLE["primary_text_color"], font=STYLE["body_font"]):
        item = QtWidgets.QGraphicsTextItem(text)
        item.setDefaultTextColor(QtGui.QColor(color))
        item.setFont(QtGui.QFont(font[0], font[1], font[2] if len(font) > 2 else 400))
        item.setPos(*pos)
        self.scene.addItem(item)
        return item

    def _create_left_sidebar(self):
        width = WINDOW_W * LEFT_SIDEBAR_W_RATIO - 20
        self.scene.addItem(create_sidebar(10, width))

        self._create_text_item("INFO", (20, 20), STYLE["secondary_text_color"], STYLE["title_font"])
        self.position_text = self._create_text_item("Position: --, --", (20, 60))
        self.distance_text = self._create_text_item("Distance: 0.00 m", (20, 90))
        self.time_text     = self._create_text_item("Time: --:--:--", (20, 120))

    def handle_serial_error(self, message):
        self.status_bar.showMessage(message)
        self.status_bar.setStyleSheet(
            "background-color: #aa0000; color: white; font: 11pt 'Consolas';"
        )

    def update_tag_data(self, data_packet):
        """Reagiert auf neue Tag-Daten und aktualisiert UI."""
        self.tag.update_position(
            data_packet["x"],
            data_packet["y"],
            data_packet["z"],
            safespace_zone
        )

        pt = self.canvas.to_canvas_coords(self.tag.x, self.tag.y)
        if self.record_trail:
            if self.trail_path.isEmpty():
                self.trail_path.moveTo(pt)
            else:
                self.trail_path.lineTo(pt)
            self.trail_item.setPath(self.trail_path)
        self.point_item.setPos(pt)

        self.position_text.setPlainText(f"Position: {self.tag.x:.2f}, {self.tag.y:.2f}")
        dist = self.tag.distance_tracker.total_distance
        self.distance_text.setPlainText(f"Distance: {dist:.2f} m")

        self.status_bar.showMessage(f"[{self.tag.id}] {data_packet}")

    def update_time(self):
        now = time.localtime()
        self.time_text.setPlainText(f"Time: {now.tm_hour:02d}:{now.tm_min:02d}:{now.tm_sec:02d}")

    def clear_trail(self):
        """Löscht Pfad und Distanzzähler."""
        self.trail_path = QtGui.QPainterPath()
        self.trail_item.setPath(self.trail_path)
        self.tag.distance_tracker.reset()
