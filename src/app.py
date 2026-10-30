import sys
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QObject, QThread, Signal
from src import config
from src.ai_service import AIService, ImprovementResult
from src.clipboard_service import ClipboardService
from src.hotkey_service import HotkeyListener
from src.ui.overlay_window import OverlayWindow
from src.ui.tray_icon import TrayIcon
from src.ui.settings_dialog import SettingsDialog


class AIWorker(QThread):
    # Eigener Name: "finished" würde das Thread-Ende-Signal von QThread verdecken
    done = Signal(object, object)
    error = Signal(object, str)

    def __init__(self, ai_service: AIService, text: str, parent=None):
        super().__init__(parent)
        self.ai_service = ai_service
        self.text = text

    def run(self):
        try:
            result = self.ai_service.improve_text(self.text)
            self.done.emit(self, result)
        except Exception as e:
            self.error.emit(self, str(e))


def format_hotkey_for_display(hotkey_str: str) -> str:
    return (
        hotkey_str.replace("<ctrl>", "Strg")
        .replace("<alt>", "Alt")
        .replace("<shift>", "Umschalt")
        .replace("<cmd>", "Win")
        .replace("<space>", "Leertaste")
        .replace("<", "").replace(">", "")
        .replace("+", " + ")
        .upper()
    )


class SprachMausApp(QObject):
    def __init__(self):
        super().__init__()
        self.settings = config.load_settings()
        self.ai_service = AIService(self.settings["GEMINI_API_KEY"], self.settings["GEMINI_MODEL"])
        self.overlay = OverlayWindow()
        self.hotkey_display = format_hotkey_for_display(self.settings["HOTKEY"])
        self.tray = TrayIcon(self.hotkey_display)
        self.hotkey = HotkeyListener(self.settings["HOTKEY"])

        self._current_worker: AIWorker | None = None

        # Wire Signals
        self.hotkey.triggered.connect(self._handle_hotkey)
        self.hotkey.failed.connect(
            lambda msg: self.tray.showMessage("Tastenkürzel nicht aktiv", msg, TrayIcon.MessageIcon.Critical, 8000)
        )
        self.overlay.suggestion_selected.connect(self._handle_suggestion_selected)
        self.tray.trigger_test.connect(self._handle_test_sentence)
        self.tray.settings_requested.connect(self.open_settings)
        self.tray.quit_requested.connect(self._handle_quit)

    def start(self):
        self.tray.show()
        self.hotkey.start()
        self.tray.showMessage(
            "SprachMaus läuft",
            f"Markiere Text und drücke {self.hotkey_display}, um Vorschläge zu sehen.",
            TrayIcon.MessageIcon.Information,
            3000
        )
        if not self.settings["GEMINI_API_KEY"]:
            self.open_settings()

    def open_settings(self):
        dialog = SettingsDialog(self.settings, config.get_autostart())
        if not dialog.exec():
            return
        new = dialog.values()
        config.save_settings(new)
        config.set_autostart(dialog.autostart())
        self.ai_service.configure(new["GEMINI_API_KEY"], new["GEMINI_MODEL"])
        if new["HOTKEY"] != self.settings["HOTKEY"]:
            self.hotkey.change(new["HOTKEY"])
            self.hotkey_display = format_hotkey_for_display(new["HOTKEY"])
            self.tray.set_hotkey_display(self.hotkey_display)
        self.settings = new
        self.tray.showMessage("Gespeichert", f"Tastenkürzel: {self.hotkey_display}", TrayIcon.MessageIcon.Information, 2000)

    def _handle_hotkey(self):
        text = ClipboardService.get_selected_text()
        if not text or not text.strip():
            self.tray.showMessage(
                "Kein Text markiert",
                "Bitte markiere zuerst ein Wort oder einen Satz mit der Maus.",
                TrayIcon.MessageIcon.Warning,
                2000
            )
            return

        self._process_text(text)

    def _handle_test_sentence(self):
        # Beispielsatz mit typischen Fehlern: falscher Artikel ("der Auto"), falscher Fall, Rechtschreibfehler
        test_text = "Ich fahre mit der Auto nach Firma weil ich muss machen ein Prasentation."
        self._process_text(test_text)

    def _process_text(self, text: str):
        self.overlay.show_loading(text)

        # Ältere Anfragen laufen zu Ende, ihr Ergebnis wird verworfen (terminate() ist unsicher)
        worker = AIWorker(self.ai_service, text, self)
        worker.done.connect(self._on_ai_success)
        worker.error.connect(self._on_ai_error)
        worker.finished.connect(worker.deleteLater)
        self._current_worker = worker
        worker.start()

    def _on_ai_success(self, worker: AIWorker, result: ImprovementResult):
        if worker is self._current_worker:
            self.overlay.show_results(result)

    def _on_ai_error(self, worker: AIWorker, err_msg: str):
        if worker is not self._current_worker:
            return
        self.overlay.hide()
        self.tray.showMessage(
            "Fehler bei KI-Korrektur",
            f"{err_msg}\n(API-Schlüssel und Modell unter Einstellungen prüfen)",
            TrayIcon.MessageIcon.Critical,
            5000
        )

    def _handle_suggestion_selected(self, new_text: str):
        ClipboardService.replace_selected_text(new_text)

    def _handle_quit(self):
        self.hotkey.stop()
        QApplication.quit()

