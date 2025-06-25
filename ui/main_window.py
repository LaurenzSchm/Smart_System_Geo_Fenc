# ui/main_window.py

import time
from PyQt6 import QtCore, QtGui, QtWidgets
from config import WINDOW_W, WINDOW_H, STYLE, LEFT_SIDEBAR_W_RATIO, MAP_WIDTH, MAP_OFFSET_X, TARGET_TAG_ID
from models import Tag
from .components import MapCanvas, create_safebox_item, create_point_item, create_sidebar


class SafespaceWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.safebox_item = None
        
        self.tag = Tag(TARGET_TAG_ID)
        self.canvas = MapCanvas()
        self.start_time = time.time()
        
        self._setup_ui()
        self._create_layout()
        
        self.grid_items = []
        
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
        
        # Botón de rotación en la esquina inferior derecha
        self.rotate_btn = QtWidgets.QPushButton("↻", self)
        self.rotate_btn.setFixedSize(140, 36)
        self.rotate_btn.move(WINDOW_W - 160, WINDOW_H - 72)
        self.rotate_btn.setStyleSheet(
            "background-color: #222; color: #00ffcc; border-radius: 8px; font: 11pt Consolas;"
        )
        self.rotate_btn.clicked.connect(self.rotate_grid)
        self.rotate_btn.raise_()  # Asegura que esté encima


    def _create_layout(self):
        """ Erstellt und platziert alle grafischen Elemente. """
        self._draw_grid_and_zone()
        self.point_item = create_point_item()
        self.scene.addItem(self.point_item)
        self._create_left_sidebar()
        self._create_right_sidebar()
        
    def _draw_grid_and_zone(self):
        # Elimina el safebox anterior si existe
        if self.safebox_item is not None:
            self.scene.removeItem(self.safebox_item)
            self.safebox_item = None

        # Elimina líneas del grid anteriores
        for item in getattr(self, "grid_items", []):
            self.scene.removeItem(item)
        self.grid_items = []

        grid_lines = []
        pen = QtGui.QPen(QtGui.QColor(STYLE["grid_color"]), 1, QtCore.Qt.PenStyle.DotLine)
        canvas = self.canvas
        # Verticales
        for i in range(int(canvas.max_x_display) + 1):
            x_real = float(i)
            if x_real >= canvas.min_x_display:
                pt = canvas.to_canvas_coords(x_real, canvas.min_y_display)
                line = self.scene.addLine(pt.x(), 0, pt.x(), WINDOW_H, pen)
                grid_lines.append(line)
        # Horizontales
        for i in range(int(canvas.max_y_display) + 1):
            y_real = float(i)
            if y_real >= canvas.min_y_display:
                pt = canvas.to_canvas_coords(canvas.min_x_display, y_real)
                line = self.scene.addLine(MAP_OFFSET_X, pt.y(), MAP_OFFSET_X + MAP_WIDTH, pt.y(), pen)
                grid_lines.append(line)
        # Zona de seguridad
        safebox = create_safebox_item(self.canvas)
        self.scene.addItem(safebox)
        self.safebox_item = safebox
        grid_lines.append(safebox)
        self.grid_items = grid_lines
        
    def rotate_grid(self):
        """ Rota el grid y actualiza la posición del punto. """
        new_rotation = (self.canvas.rotation + 90) % 360
        self.canvas.set_rotation(new_rotation)
        self._draw_grid_and_zone()
        # Actualiza la posición del punto
        pt = self.canvas.to_canvas_coords(self.tag.x, self.tag.y)
        self.point_item.setPos(pt)


        
    def _create_text_item(self, text, pos, color=STYLE["primary_text_color"], font=STYLE["body_font"]):
        item = QtWidgets.QGraphicsTextItem(text)
        item.setDefaultTextColor(QtGui.QColor(color))
        item.setFont(QtGui.QFont(font[0], font[1], font[2] if len(font)>2 else 400))
        item.setPos(*pos)
        self.scene.addItem(item)
        return item
        
    def _create_left_sidebar(self):
        # Both sidebars will be stacked vertically on the left, each half the window height
        sidebar_width = WINDOW_W * LEFT_SIDEBAR_W_RATIO - 20
        sidebar_height = (WINDOW_H // 2) - 10

        # Top sidebar: SYSTEM STATUS
        self.scene.addItem(create_sidebar(10, sidebar_width, 10, sidebar_height))
        self._create_text_item("SYSTEM STATUS", (20, 20), STYLE["secondary_text_color"], STYLE["title_font"])
        self.signal_text = self._create_text_item("Signal: --%", (20, 60))
        self.battery_text = self._create_text_item("Battery: --%", (20, 90))
        self.uptime_text = self._create_text_item("Uptime: 00:00:00", (20, 120))

    def _create_right_sidebar(self):
        # Bottom sidebar: METRICS, placed directly below the SYSTEM STATUS sidebar
        sidebar_width = WINDOW_W * LEFT_SIDEBAR_W_RATIO - 20
        sidebar_height = (WINDOW_H // 2) - 10
        y_offset = (WINDOW_H // 2) + 10

        self.scene.addItem(create_sidebar(10, sidebar_width, y_offset, sidebar_height))
        self._create_text_item("METRICS", (20, y_offset + 10), STYLE["secondary_text_color"], STYLE["title_font"])
        self.datetime_text = self._create_text_item("Date/Time: --:--:--", (20, y_offset + 50))
        self.tagcount_text = self._create_text_item(f"Tags: 1 ({self.tag.id})", (20, y_offset + 80))
        self.datarate_text = self._create_text_item("Data Rate: -- kb/s", (20, y_offset + 110))
        
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
