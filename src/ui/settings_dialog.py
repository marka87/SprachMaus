from PySide6.QtWidgets import (
    QDialog, QFormLayout, QHBoxLayout, QComboBox, QLineEdit, QCheckBox,
    QLabel, QDialogButtonBox, QMessageBox
)
from PySide6.QtCore import Qt
from src.config import MODELS
from src.hotkey_service import is_hotkey_free

MODIFIER_CHOICES = [
    ("Strg + Alt", "<ctrl>+<alt>"),
    ("Strg + Umschalt", "<ctrl>+<shift>"),
    ("Strg + Alt + Umschalt", "<ctrl>+<alt>+<shift>"),
    ("Alt + Umschalt", "<alt>+<shift>"),
    ("Strg", "<ctrl>"),
    ("Keine (nur die Taste)", ""),
]
KEY_CHOICES = (
    [(c.upper(), c) for c in "abcdefghijklmnopqrstuvwxyz0123456789"]
    + [(f"F{n}", f"<f{n}>") for n in range(1, 13)]
    + [("Leertaste", "<space>"), ("Pause", "<pause>")]
)


def split_hotkey(hotkey_str: str) -> tuple[str, str]:
    """'<ctrl>+<alt>+s' -> ('<ctrl>+<alt>', 's')"""
    mods, _, key = hotkey_str.lower().replace(" ", "").rpartition("+")
    return mods, key


class SettingsDialog(QDialog):
    def __init__(self, settings: dict, autostart: bool, parent=None):
        super().__init__(parent)
        self.setWindowTitle("SprachMaus – Einstellungen")
        self.setMinimumWidth(460)
        # Vom Tray aus geöffnet landet der Dialog sonst gern hinter anderen Fenstern
        self.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint)
        self._active_hotkey = settings["HOTKEY"]

        form = QFormLayout(self)

        # Tastenkürzel: zwei Ausklappmenüs
        self.mods_box = QComboBox()
        self.key_box = QComboBox()
        for label, value in MODIFIER_CHOICES:
            self.mods_box.addItem(label, value)
        for label, value in KEY_CHOICES:
            self.key_box.addItem(label, value)
        mods, key = split_hotkey(settings["HOTKEY"])
        for box, value in ((self.mods_box, mods), (self.key_box, key)):
            if box.findData(value) < 0:  # von Hand in die Datei geschriebene Werte nicht verlieren
                box.addItem(value, value)
            box.setCurrentIndex(box.findData(value))

        hotkey_row = QHBoxLayout()
        hotkey_row.addWidget(self.mods_box, 2)
        hotkey_row.addWidget(QLabel("+"))
        hotkey_row.addWidget(self.key_box, 1)
        form.addRow("Tastenkürzel:", hotkey_row)
        self.hotkey_status = QLabel()
        form.addRow("", self.hotkey_status)
        self.mods_box.currentIndexChanged.connect(self._update_hotkey_status)
        self.key_box.currentIndexChanged.connect(self._update_hotkey_status)

        # API-Schlüssel
        self.key_edit = QLineEdit(settings["GEMINI_API_KEY"])
        self.key_edit.setEchoMode(QLineEdit.EchoMode.Password)
        self.key_edit.setPlaceholderText("Gemini API-Schlüssel einfügen")
        show_key = QCheckBox("anzeigen")
        show_key.toggled.connect(
            lambda on: self.key_edit.setEchoMode(QLineEdit.EchoMode.Normal if on else QLineEdit.EchoMode.Password)
        )
        key_row = QHBoxLayout()
        key_row.addWidget(self.key_edit)
        key_row.addWidget(show_key)
        form.addRow("API-Schlüssel:", key_row)
        link = QLabel('<a href="https://aistudio.google.com/apikey">Kostenlosen Schlüssel bei Google AI Studio holen</a>')
        link.setOpenExternalLinks(True)
        form.addRow("", link)

        # Modell (editierbar, falls Google neue Namen einführt)
        self.model_box = QComboBox()
        self.model_box.setEditable(True)
        self.model_box.addItems(MODELS)
        self.model_box.setCurrentText(settings["GEMINI_MODEL"])
        form.addRow("KI-Modell:", self.model_box)

        self.autostart_box = QCheckBox("Mit Windows starten")
        self.autostart_box.setChecked(autostart)
        form.addRow("", self.autostart_box)

        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Save | QDialogButtonBox.StandardButton.Cancel)
        buttons.button(QDialogButtonBox.StandardButton.Save).setText("Speichern")
        buttons.button(QDialogButtonBox.StandardButton.Cancel).setText("Abbrechen")
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        form.addRow(buttons)

        self._update_hotkey_status()

    def hotkey(self) -> str:
        return "+".join(p for p in (self.mods_box.currentData(), self.key_box.currentData()) if p)

    def _hotkey_problem(self) -> str:
        if not self.mods_box.currentData() and self.key_box.currentData() in (*"abcdefghijklmnopqrstuvwxyz0123456789", "<space>"):
            return "Ohne Strg/Alt würde diese Taste beim normalen Tippen fehlen. Bitte Strg/Alt dazunehmen."
        if self.hotkey() != self._active_hotkey and not is_hotkey_free(self.hotkey()):
            return "Dieses Kürzel nutzt schon ein anderes Programm. Bitte ein anderes wählen."
        return ""

    def _update_hotkey_status(self):
        problem = self._hotkey_problem()
        self.hotkey_status.setText(f"✖ {problem}" if problem else "✔ frei – wird abgefangen und erreicht kein anderes Programm")
        self.hotkey_status.setStyleSheet(f"color: {'#dc2626' if problem else '#16a34a'};")
        self.hotkey_status.setWordWrap(True)

    def accept(self):
        problem = self._hotkey_problem()
        if problem:
            QMessageBox.warning(self, "Tastenkürzel nicht möglich", problem)
            return
        super().accept()

    def values(self) -> dict:
        return {
            "HOTKEY": self.hotkey(),
            "GEMINI_API_KEY": self.key_edit.text().strip(),
            "GEMINI_MODEL": self.model_box.currentText().strip() or MODELS[0],
        }

    def autostart(self) -> bool:
        return self.autostart_box.isChecked()
