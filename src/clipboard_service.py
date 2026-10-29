import time
import pyperclip
from pynput.keyboard import Controller, Key

keyboard = Controller()


class ClipboardService:
    @staticmethod
    def get_selected_text(timeout_seconds: float = 0.5) -> str:
        """
        Simuliert Strg+C im aktuellen Zielfenster und liest den markierten Text aus.
        """
        old_clip = ""
        try:
            old_clip = pyperclip.paste()
        except Exception:
            pass

        # Clipboard temporär leeren, um neues Kopieren sicher zu erkennen
        try:
            pyperclip.copy("")
        except Exception:
            pass

        # Strg + C simulieren
        with keyboard.pressed(Key.ctrl):
            keyboard.press('c')
            keyboard.release('c')

        # Warten bis Zwischenablage gefüllt ist
        start_time = time.time()
        selected_text = ""
        while time.time() - start_time < timeout_seconds:
            try:
                content = pyperclip.paste()
                if content:
                    selected_text = content
                    break
            except Exception:
                pass
            time.sleep(0.04)

        # Falls nichts markiert war, alten Clipboard-Inhalt wiederherstellen
        if not selected_text and old_clip:
            try:
                pyperclip.copy(old_clip)
            except Exception:
                pass

        return selected_text

    @staticmethod
    def replace_selected_text(new_text: str):
        """
        Kopiert den neuen Text in die Zwischenablage und sendet Strg+V,
        um den markierten Text im Zielfenster zu ersetzen.
        """
        pyperclip.copy(new_text)
        time.sleep(0.05)

        with keyboard.pressed(Key.ctrl):
            keyboard.press('v')
            keyboard.release('v')
