# models.py

from config import SAFESPACE_BORDERS

class Zone:
    """ Repräsentiert eine rechteckige Zone wie den Safespace. """
    def __init__(self, name, min_x, max_x, min_y, max_y):
        self.name = name
        self.min_x = min_x
        self.max_x = max_x
        self.min_y = min_y
        self.max_y = max_y

    def contains(self, x, y):
        """ Prüft, ob eine Koordinate (x, y) innerhalb der Zone liegt. """
        return self.min_x <= x <= self.max_x and self.min_y <= y <= self.max_y

class Tag:
    """ Repräsentiert ein UWB-Tag und dessen Zustand. """
    def __init__(self, tag_id):
        self.id = tag_id
        self.x = 0.0
        self.y = 0.0
        self.z = 0.0
        self.is_in_zone = False
        self.last_update_time = 0.0

    def update_position(self, x, y, z, zone):
        """ Aktualisiert die Position und den Zonenstatus des Tags. """
        self.x = x
        self.y = y
        self.z = z
        self.is_in_zone = zone.contains(x, y)
        self.last_update_time = time.time()

# Erstelle eine globale Instanz der Sicherheitszone für einfachen Zugriff
safespace_zone = Zone(
    name="Safespace",
    min_x=SAFESPACE_BORDERS["min_x"],
    max_x=SAFESPACE_BORDERS["max_x"],
    min_y=SAFESPACE_BORDERS["min_y"],
    max_y=SAFESPACE_BORDERS["max_y"]
)
