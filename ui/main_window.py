# ui/main_window.py

import time
from PyQt6 import QtCore, QtGui, QtWidgets
from config import WINDOW_W, WINDOW_H, STYLE, LEFT_SIDEBAR_W_RATIO, MAP_WIDTH, TARGET_TAG_ID
from models import Tag
from .components import MapCanvas, draw_grid, create_safebox_item, create_point_item, create_sidebar

class SafespaceWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        
        self.tag = Tag(TARGET_TAG_ID)
        self.canvas = MapCanvas()
        self.start_time = time.time()
        
        self._setup_ui()
        self._create_layout()
        
        # Timer für UI-Updates, die nicht von Daten abhängen (z.B. Uptime)
        self.ui_timer = QtCore.QTimer(self)
        self.ui_timer.timeout.connect(self.update_timed_widgets)
        self.ui_timer.start(1000) # Update jede Sekunde

    def _setup_ui(self):
        """ Grundlegende Fensterkonfiguration. """
        self.setWindowTitle("Sci-Fi Safespace Monitor")
        self.setFixedSize(WINDOW_W, WINDOW_H + 20) # + Statusleisten-Puffer

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
        """ Erstellt und platziert alle grafischen Elemente. """
        draw_grid(self.scene, self.canvas)
        self.scene.addItem(create_safebox_item(self.canvas))
        self.point_item = create_point_item()
        self.scene.addItem(self.point_item)
        
        self._create_left_sidebar()
        self._create_right_sidebar()
        
    def _create_text_item(self, text, pos, color=STYLE["primary_text_color"], font=STYLE["body_font"]):
        item = QtWidgets.QGraphicsTextItem(text)
        item.setDefaultTextColor(QtGui.QColor(color))
        item.setFont(QtGui.QFont(font[0], font[1], font[2] if len(font)>2 else 400))
        item.setPos(*pos)
        self.scene.addItem(item)
        return item
        
    def _create_left_sidebar(self):
        width = WINDOW_W * LEFT_SIDEBAR_W_RATIO - 20
        self.scene.addItem(create_sidebar(10, width))
        self._create_text_item("SYSTEM STATUS", (20, 20), STYLE["secondary_text_color"], STYLE["title_font"])
        self.signal_text = self._create_text_item("Signal: --%", (20, 60))
        self.battery_text = self._create_text_item("Battery: --%", (20, 90))
        self.uptime_text = self._create_text_item("Uptime: 00:00:00", (20, 120))

    def _create_right_sidebar(self):
        x0 = self.canvas.to_canvas_coords(0, 0).x() + MAP_WIDTH + 10
        width = WINDOW_W * (1 - LEFT_SIDEBAR_W_RATIO - MAP_WIDTH / WINDOW_W) - 20
        self.scene.addItem(create_sidebar(x0, width))
        self._create_text_item("METRICS", (x0 + 10, 20), STYLE["secondary_text_color"], STYLE["title_font"])
        self.datetime_text = self._create_text_item("Date/Time: --:--:--", (x0 + 10, 60))
        self.tagcount_text = self._create_text_item(f"Tags: 1 ({self.tag.id})", (x0 + 10, 90))
        self.datarate_text = self._create_text_item("Data Rate: -- kb/s", (x0 + 10, 120))
    
    def handle_serial_error(self, message):
        """ Zeigt einen Fehler von der seriellen Verbindung an. """
        self.status_bar.showMessage(message)
        # Optional: Visuelles Feedback, z.B. rote Statusleiste
        self.status_bar.setStyleSheet("background-color: #aa0000; color: white; font: 11pt 'Consolas';")
        
    def update_tag_data(self, data_packet):
        """ Slot, der auf das Signal des SerialWorker reagiert. """
        self.tag.update_position(
            data_packet["x"], data_packet["y"], data_packet["z"],
            # Wir könnten hier das Zone-Objekt direkt übergeben
            # Aber der Status wird schon im Worker berechnet, was okay ist.
            # Für eine reine Trennung würde man hier prüfen: zone.contains(x,y)
        )
        self.tag.is_in_zone = data_packet["is_in_zone"]

        # UI basierend auf den neuen Daten aktualisieren
        pt = self.canvas.to_canvas_coords(self.tag.x, self.tag.y)
        self.point_item.setPos(pt)
        
        if self.tag.is_in_zone:
            color = QtGui.QColor(STYLE["tag_safe_color"])
            status_text = "● IN ZONE"
        else:
            color = QtGui.QColor(STYLE["tag_unsafe_color"])
            status_text = "● OUT OF ZONE"
            
        self.point_item.setBrush(QtGui.QBrush(color))
        self.point_item.setPen(QtGui.QPen(color, 2))
        self.point_item.graphicsEffect().setColor(color)
        
        self.status_bar.showMessage(
            f"[{self.tag.id}]  X={self.tag.x:.2f}m  Y={self.tag.y:.2f}m  →  {status_text}"
        )

    def update_timed_widgets(self):
        """ Aktualisiert Widgets, die von der Zeit abhängen. """
        # Uptime
        elapsed = int(time.time() - self.start_time)
        hrs, rem = divmod(elapsed, 3600)
        mins, secs = divmod(rem, 60)
        self.uptime_text.setPlainText(f"Uptime: {hrs:02d}:{mins:02d}:{secs:02d}")

        # Aktuelle Zeit
        now = time.localtime()
        self.datetime_text.setPlainText(f"Date/Time: {now.tm_hour:02d}:{now.tm_min:02d}:{now.tm_sec:02d}")

        # Dummy-Daten aktualisieren
        sig = int((time.time() * 10 % 100))
        bat = 100 - int((time.time() / 2) % 100)
        self.signal_text.setPlainText(f"Signal: {sig}%")
        self.battery_text.setPlainText(f"Battery: {bat}%")
