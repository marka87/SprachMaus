import os
import unittest
from unittest.mock import MagicMock

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtCore import QEvent, Qt
from PySide6.QtGui import QKeyEvent
from PySide6.QtWidgets import QApplication
from src.ai_service import ImprovementResult
from src.ui.overlay_window import OverlayWindow, PROMPT_HINT


def press(window, key):
    window.keyPressEvent(QKeyEvent(QEvent.Type.KeyPress, key, Qt.KeyboardModifier.NoModifier))


def result(english="Hello"):
    return ImprovementResult("original", "korrigiert", "formell", "locker", english, "erklärt")


class TestOverlayPrompt(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])

    def setUp(self):
        self.window = OverlayWindow()
        self.window.settings = MagicMock()  # nicht in die echten Einstellungen schreiben
        self.requested, self.selected = [], []
        self.window.prompt_requested.connect(self.requested.append)
        self.window.suggestion_selected.connect(self.selected.append)
        self.window.show_results(result())

    def test_first_press_requests_prompt_only_once(self):
        press(self.window, Qt.Key.Key_5)
        press(self.window, Qt.Key.Key_5)
        self.assertEqual(self.requested, ["original"])
        self.assertEqual(self.selected, [])

    def test_finished_prompt_is_inserted_on_next_press(self):
        press(self.window, Qt.Key.Key_5)
        self.window.show_prompt("Fertiger Prompt")
        press(self.window, Qt.Key.Key_5)
        self.assertEqual(self.selected, ["Fertiger Prompt"])
        self.assertEqual(len(self.requested), 1)

    def test_failed_prompt_can_be_retried(self):
        press(self.window, Qt.Key.Key_5)
        self.window.reset_prompt()
        self.assertEqual(self.window.prompt_card.content_lbl.text(), PROMPT_HINT)
        press(self.window, Qt.Key.Key_5)
        self.assertEqual(len(self.requested), 2)

    def test_other_cards_still_insert_directly(self):
        press(self.window, Qt.Key.Key_1)
        self.assertEqual(self.selected, ["korrigiert"])

    def test_prompt_key_follows_position_without_english(self):
        self.window.show_loading("original")
        self.window.hide()
        self.window.show_results(result(english=""))
        self.assertEqual(self.window.prompt_key, "4")
        press(self.window, Qt.Key.Key_4)
        self.assertEqual(self.requested, ["original"])


if __name__ == "__main__":
    unittest.main()
