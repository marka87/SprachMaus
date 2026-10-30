import os
import tempfile
import unittest
from pathlib import Path

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
from PySide6.QtWidgets import QApplication

from src import config
from src.ui.settings_dialog import SettingsDialog, split_hotkey

app = QApplication.instance() or QApplication([])


class TestConfig(unittest.TestCase):
    def test_save_and_load_roundtrip(self):
        with tempfile.TemporaryDirectory() as tmp:
            f = Path(tmp) / "settings.env"
            f.touch()
            self.assertEqual(config.load_settings(f), config.DEFAULTS)
            wanted = {"GEMINI_API_KEY": "abc=123", "HOTKEY": "<ctrl>+<shift>+<f9>", "GEMINI_MODEL": "gemini-3.5-flash"}
            config.save_settings(wanted, f)
            self.assertEqual(config.load_settings(f), wanted)


class TestSettingsDialog(unittest.TestCase):
    def dialog(self, hotkey="<ctrl>+<alt>+s"):
        return SettingsDialog({**config.DEFAULTS, "HOTKEY": hotkey, "GEMINI_API_KEY": "k"}, autostart=False)

    def test_split_hotkey(self):
        self.assertEqual(split_hotkey("<ctrl>+<alt>+s"), ("<ctrl>+<alt>", "s"))
        self.assertEqual(split_hotkey("<pause>"), ("", "<pause>"))

    def test_dropdowns_build_hotkey(self):
        d = self.dialog("<ctrl>+<shift>+<f9>")
        self.assertEqual(d.hotkey(), "<ctrl>+<shift>+<f9>")
        d.mods_box.setCurrentIndex(d.mods_box.findData("<ctrl>+<alt>"))
        d.key_box.setCurrentIndex(d.key_box.findData("k"))
        self.assertEqual(d.values()["HOTKEY"], "<ctrl>+<alt>+k")
        self.assertEqual(d.values()["GEMINI_API_KEY"], "k")

    def test_letter_without_modifier_is_rejected(self):
        d = self.dialog()
        d.mods_box.setCurrentIndex(d.mods_box.findData(""))
        self.assertIn("Tippen", d._hotkey_problem())
        d.key_box.setCurrentIndex(d.key_box.findData("<pause>"))
        self.assertNotIn("Tippen", d._hotkey_problem())


if __name__ == "__main__":
    unittest.main()
