import sys
from PySide6.QtWidgets import QApplication
from src.app import SprachMausApp


def main():
    app = QApplication(sys.argv)
    # Verhindert, dass die App beendet wird, wenn das Overlay geschlossen wird
    app.setQuitOnLastWindowClosed(False)

    sprach_maus = SprachMausApp()
    sprach_maus.start()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
