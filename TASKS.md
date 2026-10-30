# SprachMaus – Aufgabenliste (TASKS.md)

Ein intelligenter Schreibassistent für Windows, der Nicht-Muttersprachlern beim Verfassen deutscher (und englischer) Texte in allen Anwendungen (Outlook, Teams, Slack, Word, Browser etc.) hilft.

---

## 🎯 Kernziele & Funktionsweise

1. **Markieren & Verbessern (KI-gestützt):**
   - Text in beliebigem Fenster markieren -> Tastenkürzel (z. B. `Strg + Alt + S` oder konfigurierbar).
   - Schwebendes Fenster öffnet sich mit Sofort-Vorschlägen:
     - 🟢 **Grammatik & Rechtschreibung** (inkl. richtiger Artikel: *der / die / das*, Dativ/Akkusativ, Präpositionen).
     - 👔 **Büro / Formell** (für Vorgesetzte, Kunden, offizielle E-Mails).
     - 💬 **Locker / Freundlich** (für Chat, Slack, Teams).
     - 🇬🇧 **Übersetzen** (Deutsch ↔ Englisch).
   - Enter oder Klick ersetzt den markierten Text direkt im Zielprogramm.

2. **Live-Korrektur beim Tippen (Handy-Style):**
   - Häufige Tippfehler und Wortendrehungen automatisch bei Leertaste korrigieren (per lokaler Wortliste/SymSpell).

---

## 📋 To-Do Liste

### Phase 1: MVP – "Markieren & Verbessern" (Erledigt ✅)
- [x] **1.1 Projekt-Setup**
  - [x] Python venv & Abhängigkeiten eingerichtet (`PySide6`, `pynput`, `pyperclip`, `google-genai`, `python-dotenv`)
  - [x] `.env`-Unterstützung für den Gemini API-Schlüssel
- [x] **1.2 Globaler Hotkey & Text-Erfassung**
  - [x] Hintergrund-Listener für Hotkey (`Strg + Alt + S` bzw. `<ctrl>+<alt>+s`)
  - [x] Sicheres Kopieren des aktuell markierten Texts (`Ctrl+C` per Win32 Simulation)
- [x] **1.3 KI-Prompt-Engine (Gemini Flash)**
  - [x] Hochpräziser Prompt für deutsche Grammatik (*der/die/das*, Fälle, Endungen)
  - [x] Strukturierte Ausgabe (Korrektur, Formell, Locker, Englisch + kurze Lernerklärung)
  - [x] Caching & niedrige Latenz
- [x] **1.4 Modernes Floating-Overlay (UI)**
  - [x] Randloses, modernes Schwebefenster an Mausposition (Dark Fluent UI)
  - [x] Vorschläge mit Tastatur-Navigation (Tasten `1-4` oder Klick zum Übernehmen)
  - [x] Schnelles Einfügen (`Ctrl+V` ins Zielfenster)
- [x] **1.5 System-Tray Icon**
  - [x] Icon im Windows-Infobereich (Tray) mit Schnelltest & Beenden

---

### Phase 2: Live-Autokorrektur & Wort-Vorschläge (Handy-Style) [In Planung]
- [ ] **2.1 Tastatur-Hook für Wort-Erkennung**
  - [ ] Erfassen des getippten Wortes bis zum Leerzeichen/Interpunktion
- [ ] **2.2 Lokaler Spellchecker (SymSpell / Hunspell)**
  - [ ] Deutsche Wörterbuchdatenbank ohne Cloud-Latenz (< 5 ms)
  - [ ] Automatisches Ersetzen bekannter Buchstabendreher
- [ ] **2.3 Inline-Vorschlags-Popup (Optional)**
  - [ ] Mini-Leiste über dem Cursor mit 3 Wort-Vorschlägen (wie Smartphone-Tastatur)

---

### Phase 3: Mehrsprachigkeit & Benutzeranpassung [In Planung]
- [ ] **3.1 Englisch-Support**
  - [x] Übersetzung ins Englische bereits im Overlay integriert
  - [ ] Vollständige englische Grammatikkorrektur (automatische Spracherkennung)
- [ ] **3.2 Eigenes Wörterbuch & Firmenjargon**
  - [ ] Wörter/Fachbegriffe zur Ignorierliste hinzufügen
- [x] **3.3 Windows-Autostart & Installer**
  - [x] Option "Mit Windows starten"
  - [x] Standalone `.exe` bauen (PyInstaller)
- [x] **3.4 Einstellungsfenster** (Kürzel per Ausklappmenü mit Belegt-Prüfung, API-Schlüssel, Modell, Autostart)

---

## 📌 Aktueller Status
- [x] Phase 1 MVP fertiggestellt und einsatzbereit.
- [ ] **Nächster Schritt:** Im Alltag testen. Offen: Zwischenablage nach dem Ersetzen wiederherstellen.

