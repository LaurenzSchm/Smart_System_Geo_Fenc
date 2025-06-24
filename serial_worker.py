# serial_worker.py

import time
import re
import serial
from PyQt6.QtCore import QObject, pyqtSignal
from config import SERIAL_PORT, BAUD_RATE, TARGET_TAG_ID

class SerialWorker(QObject):
    """
    Liest in einem Thread von der seriellen Schnittstelle,
    zeigt alle Rohdaten im Terminal und parst nur die Zeilen,
    die das TARGET_TAG_ID enthalten.
    """
    tag_data_received = pyqtSignal(dict)
    connection_failed = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.running = True
        # Einfacher Regex: sucht "91B2[<x>,<y>,<z>"
        self._pattern = re.compile(
            rf"{re.escape(TARGET_TAG_ID)}\[(?P<x>[-\d\.]+),(?P<y>[-\d\.]+),(?P<z>[-\d\.]+)"
        )

    def run(self):
        try:
            ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
            print(f"[SerialWorker] Port {SERIAL_PORT} geöffnet @ {BAUD_RATE} Baud")
        except serial.SerialException as e:
            self.connection_failed.emit(f"FEHLER: Konnte {SERIAL_PORT} nicht öffnen: {e}")
            return

        while self.running:
            try:
                raw_line = ser.readline().decode('ascii', errors='ignore').strip()
                if not raw_line:
                    time.sleep(0.01)
                    continue

                # Debug: alle Rohdaten anzeigen
                print(f"[SerialWorker] RAW: {raw_line}")

                # Suchen, ob unser Tag drinsteht
                m = self._pattern.search(raw_line)
                if not m:
                    continue

                # Koordinaten extrahieren
                x = float(m.group("x"))
                y = float(m.group("y"))
                z = float(m.group("z"))

                data_packet = {"id": TARGET_TAG_ID, "x": x, "y": y, "z": z}

                # Debug: nur unser Tag
                print(f"[SerialWorker] PARSED ({TARGET_TAG_ID}): {data_packet}")

                # Signal an die GUI
                self.tag_data_received.emit(data_packet)

            except (ValueError, IndexError):
                # fehlerhafte Parses ignorieren
                continue
            except serial.SerialException:
                self.connection_failed.emit("Serielle Verbindung verloren.")
                break

        ser.close()
        print("Serial Worker beendet.")

    def stop(self):
        self.running = False
