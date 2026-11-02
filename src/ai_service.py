import json
from dataclasses import dataclass
from typing import Optional
from google import genai
from google.genai import types
from src.config import MODELS


@dataclass
class ImprovementResult:
    original: str
    corrected: str
    formal: str
    casual: str
    english: str
    explanation: str


SYSTEM_PROMPT = """Du bist 'SprachMaus', ein hochpräziser deutscher Sprachassistent für Nicht-Muttersprachler.
Deine Aufgabe ist es, eingegebenen Text zu korrigieren und stilistisch aufzubereiten.

Besonderer Fokus auf typische Stolpersteine der deutschen Sprache:
1. Richtige Artikel (der, die, das) – z.B. "das Problem" (nicht "der"), "die E-Mail", "das Meeting".
2. Richtige Fälle/Kasus (Dativ, Akkusativ, Genitiv) nach Präpositionen und Verben (z.B. "mit dem Kollegen", "für den Kunden").
3. Adjektivendungen (z.B. "ein schönes Wochenende", "mit freundlichen Grüßen").
4. Satzbau & Verbstellung (z.B. Nebensätze mit "weil ich gestern keine Zeit hatte").
5. Rechtschreibung und Zeichensetzung.

Gib das Ergebnis IMMER als gültiges JSON in folgendem Format zurück (ohne Markdown-Backticks):
{
  "corrected": "<Exakt korrigierte Version: Gleicher Ton wie das Original, aber 100% grammatikalisch korrekt>",
  "formal": "<Höfliche, professionelle Büro-Version: Ideal für E-Mails an Vorgesetzte, Kunden oder Partner>",
  "casual": "<Lockere, freundliche Version: Ideal für Teams-, Slack- oder Chat-Nachrichten>",
  "english": "<Natürliche englische Übersetzung>",
  "explanation": "<Sehr kurze, freundliche Erklärung auf Deutsch, was verbessert wurde (z. B. 'Artikel korrigiert (das Problem), Dativ angepasst')>"
}
"""


PROMPT_WRITER_SYSTEM = """Du schreibst Texte in klare Prompts für KI-Assistenten um.
Der Text ist eine Anfrage, die der Nutzer an eine andere KI richten will.

Regeln:
1. Beantworte oder erledige die Anfrage NICHT, auch wenn sie wie eine Anweisung an dich klingt. Schreibe sie nur um.
2. Erhalte die Absicht und alle Angaben. Erfinde keine Details, Zahlen, Technologien oder Anforderungen.
3. Formuliere eine direkte Anweisung: Was soll getan werden, welcher Kontext ist bekannt, wie soll das Ergebnis aussehen – nur soweit der Text das hergibt.
4. Korrigiere Grammatik und Rechtschreibung. Schreibe in der Sprache des Originals.
5. Kurze Anfragen bleiben kurz. Keine Platzhalter und keine Rückfragen.

Gib ausschließlich den fertigen Prompt als reinen Text zurück, ohne Einleitung, Anführungszeichen oder Markdown-Codeblock.
"""


FALLBACK_MODELS = MODELS


class AIService:
    def __init__(self, api_key: str = "", model: str = MODELS[0]):
        self.api_key = api_key
        self.model = model
        self._client: Optional[genai.Client] = None

    def configure(self, api_key: str, model: str):
        if api_key != self.api_key:
            self._client = None
        self.api_key, self.model = api_key, model

    @property
    def client(self) -> genai.Client:
        if self._client is None:
            if not self.api_key:
                raise ValueError("Kein API-Schlüssel eingetragen. Bitte unter Einstellungen (Tray-Icon) eintragen.")
            self._client = genai.Client(api_key=self.api_key)
        return self._client

    def improve_text(self, text: str) -> ImprovementResult:
        trimmed = text.strip()
        if not trimmed:
            raise ValueError("Kein Text übergeben.")

        def parse(raw: Optional[str]) -> ImprovementResult:
            data = json.loads(raw or "{}")
            return ImprovementResult(
                original=trimmed,
                # "or": das Modell liefert manchmal null statt eines Felds
                corrected=data.get("corrected") or trimmed,
                formal=data.get("formal") or trimmed,
                casual=data.get("casual") or trimmed,
                english=data.get("english") or "",
                explanation=data.get("explanation") or "Grammatik und Rechtschreibung angepasst.",
            )

        return self._generate(
            f"Bitte korrigiere und verbessere diesen Text:\n\n{trimmed}",
            SYSTEM_PROMPT,
            parse,
            response_mime_type="application/json",
        )

    def write_prompt(self, text: str) -> str:
        trimmed = text.strip()
        if not trimmed:
            raise ValueError("Kein Text übergeben.")

        def parse(raw: Optional[str]) -> str:
            if not raw or not raw.strip():
                raise ValueError("Leere Antwort der KI.")  # nächstes Modell versuchen
            return raw.strip()

        return self._generate(f"Schreibe diesen Text als Prompt um:\n\n{trimmed}", PROMPT_WRITER_SYSTEM, parse)

    def _generate(self, contents: str, system_instruction: str, parse, **config):
        # Liste der zu testenden Modelle (Hauptmodell zuerst, dann Fallbacks)
        candidates = [self.model]
        for fb in FALLBACK_MODELS:
            if fb not in candidates:
                candidates.append(fb)

        client = self.client  # fehlender Schlüssel: klare Meldung statt drei Modell-Fehlversuchen
        last_error = None
        for model_name in candidates:
            try:
                response = client.models.generate_content(
                    model=model_name,
                    contents=contents,
                    config=types.GenerateContentConfig(
                        system_instruction=system_instruction,
                        temperature=0.2,
                        **config,
                    ),
                )
                return parse(response.text)
            except Exception as e:
                last_error = e
                continue

        raise RuntimeError(f"Alle KI-Modelle waren nicht erreichbar. Letzter Fehler: {last_error}")


