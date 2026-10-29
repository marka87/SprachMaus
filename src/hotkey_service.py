import threading
from typing import Callable
from pynput import keyboard
from PySide6.QtCore import QObject, Signal


class HotkeyListener(QObject):
    triggered = Signal()

    def __init__(self, hotkey_str: str = "<alt>+s"):
        super().__init__()
        self.hotkey_str = hotkey_str
        self._listener = None
        self._thread = None

    def _on_hotkey(self):
        self.triggered.emit()

    def start(self):
        hotkeys = {
            self.hotkey_str: self._on_hotkey
        }
        self._listener = keyboard.GlobalHotKeys(hotkeys)
        self._listener.start()

    def stop(self):
        if self._listener:
            self._listener.stop()
