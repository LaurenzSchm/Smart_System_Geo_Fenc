import time
import math
from PyQt6 import QtCore, QtGui, QtWidgets
from config import WINDOW_W, WINDOW_H, STYLE, LEFT_SIDEBAR_W_RATIO, MAP_WIDTH, TARGET_TAG_ID
from models import Tag, safespace_zone
from .components import MapCanvas, draw_grid, create_safebox_item, create_point_item, create_sidebar

class SafespaceWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()

        # Tag mit DistanceTracker
        self.tag = Tag(TARGET_TAG_ID)
        self.canvas = MapCanvas()

        self._setup_ui()
        self._create_layout()

        # Pfad-Trail initialisieren
        self.trail_path = QtGui.QPainterPath()
        self.trail_item = self.scene.addPath(
            self.trail_path,
            QtGui.QPen(QtGui.QColor("#ffff00"), 2)
        )
        self.record_trail = True

        # Schwellenwert für Bewegungen (in Metern)
        self.min_move_threshold = 0.5
        self.last_pos = None
        self.distance_accumulated = 0.0

        # Timer nur für Uhrzeit
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

        # Marker für Tag
        self.point_item = create_point_item()
        self.scene.addItem(self.point_item)

        # Seitenleiste
        self._create_left_sidebar()

        # Reset-Trail Button
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

        # Info-Labels
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
        # 1) Position & Zone & Distanz updaten
        self.tag.update_position(
            data_packet["x"],
            data_packet["y"],
            data_packet["z"],
            safespace_zone
        )

        # 2) Schwellenwert-basierte Distanz & Trail
        x, y = self.tag.x, self.tag.y
        if self.last_pos is None:
            self.last_pos = (x, y)
        else:
            dx = x - self.last_pos[0]
            dy = y - self.last_pos[1]
            dist = math.hypot(dx, dy)
            if dist >= self.min_move_threshold:
                # Distanz aufsummieren
                self.distance_accumulated += dist
                self.last_pos = (x, y)
                # Pfad zeichnen
                pt = self.canvas.to_canvas_coords(x, y)
                if self.record_trail:
                    if self.trail_path.isEmpty():
                        self.trail_path.moveTo(pt)
                    else:
                        self.trail_path.lineTo(pt)
                    self.trail_item.setPath(self.trail_path)
                self.point_item.setPos(pt)
        # Falls Movement < Threshold, nur Marker aktualisieren
        if self.distance_accumulated == 0:
            pt = self.canvas.to_canvas_coords(x, y)
            self.point_item.setPos(pt)

        # 3) Sidebar-Infos aktualisieren
        self.position_text.setPlainText(
            f"Position: {self.tag.x:.2f}, {self.tag.y:.2f}"
        )
        self.distance_text.setPlainText(f"Distance: {self.distance_accumulated:.2f} m")

        # 4) Status-Bar mit Rohdaten
        self.status_bar.showMessage(f"[{self.tag.id}] {data_packet}")

    def update_time(self):
        """Aktualisiert nur die Uhrzeit-Anzeige."""
        now = time.localtime()
        self.time_text.setPlainText(
            f"Time: {now.tm_hour:02d}:{now.tm_min:02d}:{now.tm_sec:02d}"
        )

    def clear_trail(self):
        """Löscht den gezeichneten Pfad und setzt Distanz zurück."""
        self.trail_path = QtGui.QPainterPath()
        self.trail_item.setPath(self.trail_path)
        self.last_pos = None
        self.distance_accumulated = 0.0
        self.distance_text.setPlainText("Distance: 0.00 m")
