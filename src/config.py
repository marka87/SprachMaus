import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
HOTKEY = os.getenv("HOTKEY", "<alt>+s")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
