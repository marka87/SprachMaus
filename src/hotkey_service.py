import ctypes
import threading
from ctypes import wintypes
from PySide6.QtCore import QObject, Signal

user32 = ctypes.windll.user32
kernel32 = ctypes.windll.kernel32

WM_HOTKEY = 0x0312
WM_QUIT = 0x0012
MOD_NOREPEAT = 0x4000
MODIFIERS = {"<alt>": 0x1, "<ctrl>": 0x2, "<shift>": 0x4, "<cmd>": 0x8}
NAMED_KEYS = {"<space>": 0x20, "<pause>": 0x13, "<scroll_lock>": 0x91, "<insert>": 0x2D}


def parse_hotkey(hotkey_str: str) -> tuple[int, int]:
    """Wandelt z. B. '<ctrl>+<alt>+s' in (Modifier-Flags, Virtual-Key-Code) für RegisterHotKey."""
    mods, vk = 0, None
    for part in hotkey_str.lower().replace(" ", "").split("+"):
        if part in MODIFIERS:
            mods |= MODIFIERS[part]
        elif part in NAMED_KEYS:
            vk = NAMED_KEYS[part]
        elif len(part) == 1 and part.isascii() and part.isalnum():
            vk = ord(part.upper())
        elif part.startswith("<f") and part.endswith(">") and part[2:-1].isdigit() and 1 <= int(part[2:-1]) <= 24:
            vk = 0x6F + int(part[2:-1])  # F1 = 0x70
        else:
            raise ValueError(f"Unbekannte Taste in HOTKEY: '{part}'")
    if vk is None:
        raise ValueError(f"HOTKEY '{hotkey_str}' enthält keine normale Taste.")
    return mods, vk


def is_hotkey_free(hotkey_str: str) -> bool:
    mods, vk = parse_hotkey(hotkey_str)
    if not user32.RegisterHotKey(None, 99, mods | MOD_NOREPEAT, vk):
        return False
    user32.UnregisterHotKey(None, 99)
    return True


class HotkeyListener(QObject):
    triggered = Signal()
    failed = Signal(str)

    def __init__(self, hotkey_str: str = "<ctrl>+<alt>+s"):
        super().__init__()
        self.hotkey_str = hotkey_str
        self._thread_id = 0

    def start(self):
        try:
            mods, vk = parse_hotkey(self.hotkey_str)
        except ValueError as e:
            self.failed.emit(str(e))
            return
        threading.Thread(target=self._run, args=(mods, vk), daemon=True).start()

    def _run(self, mods: int, vk: int):
        self._thread_id = kernel32.GetCurrentThreadId()
        # RegisterHotKey schluckt die Tasten: Outlook & Co. bekommen die Kombination nicht mehr zu sehen
        if not user32.RegisterHotKey(None, 1, mods | MOD_NOREPEAT, vk):
            self.failed.emit(f"{self.hotkey_str} ist schon von einem anderen Programm belegt. Bitte unter Einstellungen ein anderes Kürzel wählen.")
            return
        msg = wintypes.MSG()
        while user32.GetMessageW(ctypes.byref(msg), None, 0, 0) > 0:
            if msg.message == WM_HOTKEY:
                self.triggered.emit()
        user32.UnregisterHotKey(None, 1)

    def stop(self):
        if self._thread_id:
            user32.PostThreadMessageW(self._thread_id, WM_QUIT, 0, 0)
            self._thread_id = 0

    def change(self, hotkey_str: str):
        self.stop()
        self.hotkey_str = hotkey_str
        self.start()
