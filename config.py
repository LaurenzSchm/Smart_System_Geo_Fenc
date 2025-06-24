# config.py

# Serielle Schnittstelle
SERIAL_PORT = 'COM9'
BAUD_RATE = 115200

# Ziel-Tag ID
TARGET_TAG_ID = "91B2"

# ----------------------------------------
# GEOMETRIE & SKALIERUNG (in Metern)
# ----------------------------------------

# Anker-Positionen definieren den Gesamtbereich
ANCHOR_X0 = 0.0
ANCHOR_Y0 = 0.0
ANCHOR_X1 = 7.8
ANCHOR_Y1 = 11.6

# Sicherheitszone (1m vom Rand der Anker)
SAFESPACE_BORDERS = {
    "min_x": ANCHOR_X0 + 1.0,
    "max_x": ANCHOR_X1 - 1.0,
    "min_y": ANCHOR_Y0 + 1.0,
    "max_y": ANCHOR_Y1 - 1.0
}

# ----------------------------------------
# FENSTER- & KARTEN-LAYOUT (in Pixel)
# ----------------------------------------
WINDOW_W = 1000
WINDOW_H = 600

# Proportionen für die UI-Elemente
LEFT_SIDEBAR_W_RATIO = 0.22
MAP_W_RATIO = 0.56
RIGHT_SIDEBAR_W_RATIO = 0.22

MAP_OFFSET_X = WINDOW_W * LEFT_SIDEBAR_W_RATIO
MAP_WIDTH = WINDOW_W * MAP_W_RATIO

# ----------------------------------------
# STYLING
# ----------------------------------------
STYLE = {
    "background_color": "#0d0d0d",
    "primary_text_color": "#00ffcc",
    "secondary_text_color": "#00aaff",
    "grid_color": "#1e1e1e",
    "safe_zone_pen_color": "#00b4ff",
    "safe_zone_brush_color": "#003c64",
    "safe_zone_glow_color": "#00b4ff",
    "tag_safe_color": "#00ff64",
    "tag_unsafe_color": "#ff3232",
    "sidebar_bg_color": "#0a0a0a",
    "sidebar_border_color": "#006496",
    "title_font": ("Consolas", 12, 700), # Family, Size, Weight
    "body_font": ("Consolas", 10)
}

