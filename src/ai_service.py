import json
from dataclasses import dataclass
from typing import Optional
from google import genai
from google.genai import types
from src.config import GEMINI_API_KEY, GEMINI_MODEL


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


class AIService:
    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        self.api_key = api_key or GEMINI_API_KEY
        self.model = model or GEMINI_MODEL
        self._client: Optional[genai.Client] = None

    @property
    def client(self) -> genai.Client:
        if self._client is None:
            if not self.api_key:
                raise ValueError("GEMINI_API_KEY ist nicht gesetzt! Bitte in .env eintragen.")
            self._client = genai.Client(api_key=self.api_key)
        return self._client

    def improve_text(self, text: str) -> ImprovementResult:
        trimmed = text.strip()
        if not trimmed:
            raise ValueError("Kein Text übergeben.")

        response = self.client.models.generate_content(
            model=self.model,
            contents=f"Bitte korrigiere und verbessere diesen Text:\n\n{trimmed}",
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM_PROMPT,
                temperature=0.2,
                response_mime_type="application/json",
            ),
        )

        raw = response.text or "{}"
        data = json.loads(raw)

        return ImprovementResult(
            original=trimmed,
            corrected=data.get("corrected", trimmed),
            formal=data.get("formal", trimmed),
            casual=data.get("casual", trimmed),
            english=data.get("english", ""),
            explanation=data.get("explanation", "Grammatik und Rechtschreibung angepasst."),
        )

