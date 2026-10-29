import sys
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QObject, QThread, Signal
from src.config import HOTKEY
from src.ai_service import AIService, ImprovementResult
from src.clipboard_service import ClipboardService
from src.hotkey_service import HotkeyListener
from src.ui.overlay_window import OverlayWindow
from src.ui.tray_icon import TrayIcon


class AIWorker(QThread):
    finished = Signal(object)
    error = Signal(str)

    def __init__(self, ai_service: AIService, text: str):
        super().__init__()
        self.ai_service = ai_service
        self.text = text

    def run(self):
        try:
            result = self.ai_service.improve_text(self.text)
            self.finished.emit(result)
        except Exception as e:
            self.error.emit(str(e))


class SprachMausApp(QObject):
    def __init__(self):
        super().__init__()
        self.ai_service = AIService()
        self.overlay = OverlayWindow()
        self.tray = TrayIcon()
        self.hotkey = HotkeyListener(HOTKEY)

        self._current_worker: AIWorker | None = None

        # Wire Signals
        self.hotkey.triggered.connect(self._handle_hotkey)
        self.overlay.suggestion_selected.connect(self._handle_suggestion_selected)
        self.tray.trigger_test.connect(self._handle_test_sentence)
        self.tray.quit_requested.connect(self._handle_quit)

    def start(self):
        self.tray.show()
        self.hotkey.start()
        self.tray.showMessage(
            "SprachMaus läuft",
            f"Markiere Text und drücke {HOTKEY}, um Vorschläge zu sehen.",
            TrayIcon.MessageIcon.Information,
            3000
        )

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

        if self._current_worker and self._current_worker.isRunning():
            self._current_worker.terminate()

        self._worker = AIWorker(self.ai_service, text)
        self._worker.finished.connect(self._on_ai_success)
        self._worker.error.connect(self._on_ai_error)
        self._worker.start()

    def _on_ai_success(self, result: ImprovementResult):
        self.overlay.show_results(result)

    def _on_ai_error(self, err_msg: str):
        self.overlay.hide()
        self.tray.showMessage(
            "Fehler bei KI-Korrektur",
            f"{err_msg}\n(Ist der API-Schlüssel in .env eingetragen?)",
            TrayIcon.MessageIcon.Critical,
            5000
        )

    def _handle_suggestion_selected(self, new_text: str):
        ClipboardService.replace_selected_text(new_text)

    def _handle_quit(self):
        self.hotkey.stop()
        QApplication.quit()
