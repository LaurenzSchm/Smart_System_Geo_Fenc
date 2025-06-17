# serial_worker.py

import time
import serial
from PyQt6.QtCore import QObject, pyqtSignal

from config import SERIAL_PORT, BAUD_RATE, TARGET_TAG_ID
from models import safespace_zone

class SerialWorker(QObject):
    """
    Liest in einem separaten Thread von der seriellen Schnittstelle
    und sendet die Daten über ein PyQt-Signal an die GUI.
    """
    # Signal: sendet ein Dictionary mit den Tag-Daten
    tag_data_received = pyqtSignal(dict)
    connection_failed = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.running = True

    def run(self):
        """ Die Hauptschleife des Workers. """
        try:
            ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
        except serial.SerialException as e:
            self.connection_failed.emit(f"FEHLER: Konnte {SERIAL_PORT} nicht öffnen: {e}")
            return

        while self.running:
            try:
                raw_line = ser.readline().decode('ascii', errors='ignore').strip()
                if not raw_line:
                    time.sleep(0.01)
                    continue

                # Beispiel-Format: "POS,0,91B2,5.70,6.85,-0.65,64,x00"
                parts = raw_line.split(',')
                if len(parts) >= 6 and parts[0] == 'POS':
                    tag_id = parts[2]
                    if tag_id != TARGET_TAG_ID:
                        continue

                    x = float(parts[3])
                    y = float(parts[4])
                    z = float(parts[5])

                    # Erstelle ein sauberes Datenpaket und sende es per Signal
                    data_packet = {
                        "id": tag_id,
                        "x": x,
                        "y": y,
                        "z": z,
                        "is_in_zone": safespace_zone.contains(x, y)
                    }
                    self.tag_data_received.emit(data_packet)

            except (ValueError, IndexError):
                # Ignoriere fehlerhafte Zeilen
                continue
            except serial.SerialException:
                self.connection_failed.emit("Serielle Verbindung verloren.")
                break

        ser.close()
        print("Serial Worker beendet.")

    def stop(self):
        self.running = False
