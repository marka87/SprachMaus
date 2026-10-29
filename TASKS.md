# SprachMaus – Aufgabenliste (TASKS.md)

Ein intelligenter Schreibassistent für Windows, der Nicht-Muttersprachlern beim Verfassen deutscher (und englischer) Texte in allen Anwendungen (Outlook, Teams, Slack, Word, Browser etc.) hilft.

---

## 🎯 Kernziele & Funktionsweise

1. **Markieren & Verbessern (KI-gestützt):**
   - Text in beliebigem Fenster markieren -> Tastenkürzel (z. B. `Alt + S` oder doppelt `Strg`).
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

### Phase 1: MVP – "Markieren & Verbessern" (Priorität 1)
- [ ] **1.1 Projekt-Setup**
  - [ ] Python venv & Abhängigkeiten einrichten (`PySide6`, `pynput`, `pyperclip`, `google-genai` / Gemini API)
  - [ ] `.env`-Unterstützung für den Gemini API-Schlüssel
- [ ] **1.2 Globaler Hotkey & Text-Erfassung**
  - [ ] Hintergrund-Listener für Hotkey (z. B. `Alt + S` oder konfigurierbar)
  - [ ] Sicheres Kopieren des aktuell markierten Texts (`Ctrl+C` per Win32 Simulation)
- [ ] **1.3 KI-Prompt-Engine (Gemini Flash)**
  - [ ] Schneller Prompt für deutsche Grammatik (*der/die/das*, Fälle, Endungen)
  - [ ] Strukturierte Ausgabe (Korrektur, Formell, Locker, Erklärung warum geändert)
  - [ ] Caching & niedrige Latenz (Ziel: < 1 Sekunde Antwortzeit)
- [ ] **1.4 Modernes Floating-Overlay (UI)**
  - [ ] Randloses, modernes Schwebefenster an Mausposition (Dark / Light Mode)
  - [ ] Vorschläge mit Tastatur-Navigation (Pfeiltasten + `Enter` zum Übernehmen)
  - [ ] Schnelles Einfügen (`Ctrl+V` ins Zielfenster)
- [ ] **1.5 System-Tray Icon**
  - [ ] Icon im Windows-Infobereich (Tray) zum Beenden, Pausieren und Konfigurieren

---

### Phase 2: Live-Autokorrektur & Wort-Vorschläge (Handy-Style)
- [ ] **2.1 Tastatur-Hook für Wort-Erkennung**
  - [ ] Erfassen des getippten Wortes bis zum Leerzeichen/Interpunktion
- [ ] **2.2 Lokaler Spellchecker (SymSpell / Hunspell)**
  - [ ] Deutsche Wörterbuchdatenbank ohne Cloud-Latenz (< 5 ms)
  - [ ] Automatisches Ersetzen bekannter Buchstabendreher
- [ ] **2.3 Inline-Vorschlags-Popup (Optional)**
  - [ ] Mini-Leiste über dem Cursor mit 3 Wort-Vorschlägen (wie Smartphone-Tastatur)

---

### Phase 3: Mehrsprachigkeit & Benutzeranpassung
- [ ] **3.1 Englisch-Support**
  - [ ] Automatische Spracherkennung (Deutsch vs. Englisch)
  - [ ] Englische Grammatik & Umformulierungen (Professional vs. Casual)
- [ ] **3.2 Eigenes Wörterbuch & Firmenjargon**
  - [ ] Wörter/Fachbegriffe zur Ignorierliste hinzufügen
- [ ] **3.3 Windows-Autostart & Installer**
  - [ ] Option "Mit Windows starten"
  - [ ] Verpackung als `.exe` (PyInstaller / Nuitka)

---

## 📌 Aktueller Status
- [x] Projektidee & Anforderungsanalyse abgeschlossen
- [x] `TASKS.md` erstellt
- [ ] **Nächster Schritt:** Phase 1.1 & 1.2 – Grundgerüst bauen und testen.
