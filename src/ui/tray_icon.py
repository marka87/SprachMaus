from PySide6.QtWidgets import QSystemTrayIcon, QMenu
from PySide6.QtGui import QIcon, QPixmap, QPainter, QColor, QFont
from PySide6.QtCore import Qt, Signal


def create_mouse_icon() -> QIcon:
    """Erzeugt ein einfaches, elegantes Icon für den System-Tray ohne externe Bilddatei."""
    pixmap = QPixmap(64, 64)
    pixmap.fill(Qt.GlobalColor.transparent)

    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)

    # Hintergrundkreis
    painter.setBrush(QColor("#0284c7"))
    painter.setPen(Qt.PenStyle.NoPen)
    painter.drawEllipse(4, 4, 56, 56)

    # Buchstabe / Symbol
    painter.setPen(QColor("#ffffff"))
    font = QFont("Segoe UI Emoji", 26)
    font.setBold(True)
    painter.setFont(font)
    painter.drawText(pixmap.rect(), Qt.AlignmentFlag.AlignCenter, "🐭")
    painter.end()

    return QIcon(pixmap)


class TrayIcon(QSystemTrayIcon):
    trigger_test = Signal()
    settings_requested = Signal()
    quit_requested = Signal()

    def __init__(self, hotkey_display: str = "Strg+Alt+S", parent=None):
        super().__init__(create_mouse_icon(), parent)
        self.set_hotkey_display(hotkey_display)

        menu = QMenu()
        menu.setStyleSheet("""
            QMenu {
                background-color: #0f172a;
                color: #f8fafc;
                border: 1px solid #334155;
                border-radius: 8px;
                padding: 4px;
            }
            QMenu::item {
                padding: 6px 20px;
                border-radius: 4px;
            }
            QMenu::item:selected {
                background-color: #1e293b;
                color: #38bdf8;
            }
        """)

        title_action = menu.addAction("🐭 SprachMaus (Aktiv)")
        title_action.setEnabled(False)
        menu.addSeparator()

        test_action = menu.addAction("Beispielsatz korrigieren")
        test_action.triggered.connect(self.trigger_test.emit)

        settings_action = menu.addAction("Einstellungen …")
        settings_action.triggered.connect(self.settings_requested.emit)

        menu.addSeparator()
        quit_action = menu.addAction("Beenden")
        quit_action.triggered.connect(self.quit_requested.emit)

        self.setContextMenu(menu)
        self.menu = menu  # Referenz halten, sonst räumt Python das Menü weg

    def set_hotkey_display(self, hotkey_display: str):
        self.setToolTip(f"SprachMaus – Dein KI-Schreibassistent ({hotkey_display})")

