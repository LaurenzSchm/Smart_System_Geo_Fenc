# serial_worker.py

import time
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

                # ----- AB HIER ANPASSUNG FÜR DEIN FORMAT -----
                # Erwarte Format: POS,0,91B2,0.47,7.73,0.29,61,x0B
                if TARGET_TAG_ID in raw_line:
                    parts = raw_line.split(",")
                    try:
                        idx = parts.index(TARGET_TAG_ID)
                        x = float(parts[idx + 1])
                        y = float(parts[idx + 2])
                        z = float(parts[idx + 3])
                        data_packet = {"id": TARGET_TAG_ID, "x": x, "y": y, "z": z}
                        print(f"[SerialWorker] PARSED ({TARGET_TAG_ID}): {data_packet}")
                        self.tag_data_received.emit(data_packet)
                    except (ValueError, IndexError):
                        continue
                # ----- ENDE ANPASSUNG -----

            except (ValueError, IndexError):
                continue
            except serial.SerialException:
                self.connection_failed.emit("Serielle Verbindung verloren.")
                break

        ser.close()
        print("Serial Worker beendet.")

    def stop(self):
        self.running = False

