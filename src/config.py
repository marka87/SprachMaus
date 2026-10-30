import os
import shutil
import sys
import winreg
from pathlib import Path
from dotenv import dotenv_values, set_key

BASE_DIR = Path(__file__).resolve().parent.parent
# Im Benutzerprofil statt neben dem Programm: die .exe darf nicht in ihren eigenen Ordner schreiben müssen
CONFIG_DIR = Path(os.getenv("APPDATA", Path.home())) / "SprachMaus"
CONFIG_FILE = CONFIG_DIR / "settings.env"

MODELS = ["gemini-3.5-flash-lite", "gemini-3.5-flash", "gemini-flash-latest"]
DEFAULTS = {
    "GEMINI_API_KEY": "",
    "HOTKEY": "<ctrl>+<alt>+s",
    "GEMINI_MODEL": MODELS[0],
}

RUN_KEY = r"Software\Microsoft\Windows\CurrentVersion\Run"


def load_settings(config_file: Path = CONFIG_FILE) -> dict:
    if not config_file.exists() and (BASE_DIR / ".env").exists():
        config_file.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy(BASE_DIR / ".env", config_file)  # einmalig die alte .env aus dem Projektordner übernehmen
    values = dotenv_values(config_file) if config_file.exists() else {}
    return {key: values.get(key) or default for key, default in DEFAULTS.items()}


def save_settings(settings: dict, config_file: Path = CONFIG_FILE):
    config_file.parent.mkdir(parents=True, exist_ok=True)
    config_file.touch()
    for key in DEFAULTS:
        set_key(config_file, key, settings[key], quote_mode="never")


def _start_command() -> str:
    if getattr(sys, "frozen", False):  # als SprachMaus.exe gebaut
        return f'"{sys.executable}"'
    pythonw = Path(sys.executable).with_name("pythonw.exe")
    return f'"{pythonw}" "{BASE_DIR / "main.py"}"'


def get_autostart() -> bool:
    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, RUN_KEY) as key:
            winreg.QueryValueEx(key, "SprachMaus")
            return True
    except FileNotFoundError:
        return False


def set_autostart(enabled: bool):
    # HKCU braucht keine Admin-Rechte
    with winreg.OpenKey(winreg.HKEY_CURRENT_USER, RUN_KEY, 0, winreg.KEY_SET_VALUE) as key:
        if enabled:
            winreg.SetValueEx(key, "SprachMaus", 0, winreg.REG_SZ, _start_command())
        elif get_autostart():
            winreg.DeleteValue(key, "SprachMaus")
