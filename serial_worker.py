# serial_worker.py

import time
import serial
from PyQt6.QtCore import QObject, pyqtSignal
from config import SERIAL_PORT, BAUD_RATE, TARGET_TAG_ID

class SerialWorker(QObject):
    """
    Liest in einem Thread von der seriellen Schnittstelle und parst die Daten.
    Verwendet eine robustere Methode, um POS-Zeilen zu identifizieren.
    """
    tag_data_received = pyqtSignal(dict)
    connection_failed = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.running = True

    def run(self):
        """ Die Hauptschleife des Workers. """
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
                # print(f"[SerialWorker] RAW: {raw_line}")

                # Parsen mit der split()-Methode
                parts = raw_line.split(',')
                # Erwartetes Format: "POS,irgendwas,TAG_ID,x,y,z,..."
                if len(parts) >= 6 and parts[0].upper() == 'POS' and parts[2] == TARGET_TAG_ID:
                    
                    tag_id = parts[2]
                    x = float(parts[3])
                    y = float(parts[4])
                    z = float(parts[5])

                    data_packet = {"id": tag_id, "x": x, "y": y, "z": z}

                    # Signal an die GUI senden
                    self.tag_data_received.emit(data_packet)

            except (ValueError, IndexError):
                # fehlerhafte oder unvollständige Zeilen ignorieren
                continue
            except serial.SerialException:
                self.connection_failed.emit("Serielle Verbindung verloren.")
                break

        ser.close()
        print("[SerialWorker] beendet.")

    def stop(self):
        self.running = False
