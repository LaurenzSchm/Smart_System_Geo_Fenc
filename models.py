# models.py

from __future__ import annotations
import time
import math
from config import SAFESPACE_BORDERS

class Zone:
    """Repräsentiert eine rechteckige Zone wie den Safespace."""
    def __init__(self, name: str, min_x: float, max_x: float, min_y: float, max_y: float):
        self.name = name
        self.min_x = min_x
        self.max_x = max_x
        self.min_y = min_y
        self.max_y = max_y

    def contains(self, x: float, y: float) -> bool:
        """Prüft, ob eine Koordinate (x, y) innerhalb der Zone liegt."""
        return self.min_x <= x <= self.max_x and self.min_y <= y <= self.max_y


class DistanceTracker:
    """Misst die kumulierte 2D-Strecke anhand sukzessiver Positionen."""
    THRESHOLD = 0.5  # Bewegungs-Schwellenwert in Metern

    def __init__(self):
        self._last_pos: tuple[float, float] | None = None
        self.total_distance: float = 0.0

    def update(self, x: float, y: float) -> None:
        """Hinzufügen der Distanz seit der letzten Position, Mikrobewegungen ignorieren."""
        if self._last_pos is not None:
            dx = x - self._last_pos[0]
            dy = y - self._last_pos[1]
            dist = math.hypot(dx, dy)
            if dist > self.THRESHOLD:
                self.total_distance += dist
        self._last_pos = (x, y)

    def reset(self) -> None:
        """Setzt Zähler und letzte Position zurück."""
        self._last_pos = None
        self.total_distance = 0.0


class Tag:
    """Repräsentiert ein UWB-Tag und dessen Zustand inklusive Distanz-Tracking."""
    def __init__(self, tag_id: str):
        self.id = tag_id
        self.x: float = 0.0
        self.y: float = 0.0
        self.z: float = 0.0
        self.is_in_zone: bool = False
        self.last_update_time: float = 0.0
        self.distance_tracker = DistanceTracker()

    def update_position(self, x: float, y: float, z: float, zone: 'Zone') -> None:
        """Aktualisiert Position, Zonenstatus und Distanz."""
        self.x = x
        self.y = y
        self.z = z
        self.last_update_time = time.time()
        self.is_in_zone = zone.contains(x, y)
        self.distance_tracker.update(x, y)


# Globale Instanz der Sicherheitszone
safespace_zone = Zone(
    name="Safespace",
    min_x=SAFESPACE_BORDERS["min_x"],
    max_x=SAFESPACE_BORDERS["max_x"],
    min_y=SAFESPACE_BORDERS["min_y"],
    max_y=SAFESPACE_BORDERS["max_y"]
)
