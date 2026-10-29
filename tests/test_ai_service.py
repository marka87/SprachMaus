import unittest
from unittest.mock import MagicMock
from src.ai_service import AIService, ImprovementResult


class TestAIService(unittest.TestCase):
    def test_prompt_parsing(self):
        service = AIService(api_key="mock_key")
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.text = '''{
            "corrected": "Ich fahre mit dem Auto zur Firma.",
            "formal": "Sehr geehrte Damen und Herren, ich fahre mit dem Auto zum Unternehmensstandort.",
            "casual": "Hi! Bin mit dem Auto auf dem Weg ins Büro.",
            "english": "I am driving by car to the office.",
            "explanation": "Artikel 'das Auto' im Dativ angepasst: 'mit dem Auto'."
        }'''
        mock_client.models.generate_content.return_value = mock_response
        service._client = mock_client

        res = service.improve_text("Ich fahre mit der Auto nach Firma.")
        self.assertEqual(res.corrected, "Ich fahre mit dem Auto zur Firma.")
        self.assertIn("mit dem Auto", res.explanation)
        self.assertEqual(res.english, "I am driving by car to the office.")


if __name__ == "__main__":
    unittest.main()

