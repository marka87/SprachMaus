# 🐭 SprachMaus (Windows)

Ein smarter Windows-Schreibassistent für Nicht-Muttersprachler. Verbessert E-Mails, Chats und Dokumente in Echtzeit per Tastenkürzel (`Strg + Alt + S`).

---

## ✨ Features

- **Erkennt Kontext & Artikel (*der, die, das*):**
  - Falscher Artikel: `der Problem` ➔ `das Problem`
  - Falscher Fall (Dativ/Akkusativ): `mit das Auto` ➔ `mit dem Auto`
  - Satzbau & Verbstellung: `weil ich habe keine Zeit` ➔ `weil ich keine Zeit hatte`
- **3-fach Vorschläge per Knopfdruck:**
  1. `[1]` 🟢 **Korrigiert** (Direkte Korrektur von Grammatik, Artikeln & Rechtschreibung)
  2. `[2]` 👔 **Formell / Büro** (Höflich und professionell für E-Mails an Chefs/Kunden)
  3. `[3]` 💬 **Locker / Chat** (Freundlich für Microsoft Teams, Slack oder WhatsApp)
  4. `[4]` 🇬🇧 **Englisch** (Sofortige Übersetzung)
- **Erklärungs-Funktion:** Zeigt kurz an, *warum* etwas geändert wurde (z.B. *"Artikel korrigiert: das Problem statt der Problem, Dativ nach 'mit'"*).
- **Direktes Ersetzen:** Drücke `1`, `2`, `3`, `4` oder klicke darauf – der markierte Text wird direkt im Zielprogramm (Outlook, Teams, Word, Chrome) ausgetauscht.

---

## 🚀 Schnellstart

### 1. API-Schlüssel einrichten
1. Erstelle dir kostenlos einen Gemini API-Schlüssel auf [Google AI Studio](https://aistudio.google.com/apikey).
2. Erstelle eine Datei namens `.env` im Hauptverzeichnis (oder kopiere `.env.example` nach `.env`):
   ```env
   GEMINI_API_KEY=dein_echter_api_key_hier
   HOTKEY=<ctrl>+<alt>+s
   ```

### 2. SprachMaus starten
```powershell
.\.venv\Scripts\python main.py
```

### 3. Ausprobieren
1. Öffne ein beliebiges Programm (Word, Editor, Teams, Browser).
2. Markiere einen fehlerhaften Satz, z. B.:
   > *"Ich habe gestern geschickt das E-Mail an der Chef, aber er hat nicht geantwortet."*
3. Drücke **`Strg + Alt + S`** (oder dein konfiguriertes Kürzel).
4. Wähle mit Taste `1`, `2`, `3` oder `4` deinen Wunschsatz aus – fertig!

---

## 🛠️ Geplante Erweiterungen (siehe [TASKS.md](TASKS.md))
- Lokale Handy-Style Live-Autokorrektur (symspell) ohne Cloud-Verzögerung.
- Einstellungsmenü im Tray-Icon.
- Standalone `.exe` ohne Python-Installation.

