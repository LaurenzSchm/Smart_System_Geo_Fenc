# main.py

import sys
from PyQt6 import QtWidgets
from PyQt6.QtCore import QThread

from serial_worker import SerialWorker
from ui.main_window import SafespaceWindow

def main():
    """ Hauptfunktion zum Starten der Anwendung. """
    app = QtWidgets.QApplication(sys.argv)
    
    # 1. Erstelle das Hauptfenster der GUI
    window = SafespaceWindow()

    # 2. Richte den SerialWorker in einem separaten Thread ein
    #    Dies verhindert, dass die GUI einfriert, während auf serielle Daten gewartet wird.
    thread = QThread()
    worker = SerialWorker()
    worker.moveToThread(thread)

    # 3. Verbinde die Signale und Slots
    #    - Wenn der Thread startet, rufe die 'run'-Methode des Workers auf.
    #    - Wenn der Worker Daten sendet, rufe die 'update_tag_data'-Methode des Fensters auf.
    #    - Wenn der Worker einen Fehler meldet, rufe 'handle_serial_error' auf.
    #    - Wenn der Thread beendet wird, beende auch den Worker und räume auf.
    thread.started.connect(worker.run)
    worker.tag_data_received.connect(window.update_tag_data)
    worker.connection_failed.connect(window.handle_serial_error)
    worker.connection_failed.connect(thread.quit) # Beende den Thread bei Fehler
    
    thread.finished.connect(worker.deleteLater)
    app.aboutToQuit.connect(worker.stop) # Signal zum Stoppen der Worker-Schleife
    app.aboutToQuit.connect(thread.quit)
    app.aboutToQuit.connect(thread.wait)

    # 4. Starte den Thread
    thread.start()
    
    # 5. Zeige das Fenster an und starte die App
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()

