import unittest
from unittest.mock import MagicMock
from src.ai_service import AIService, ImprovementResult, PROMPT_WRITER_SYSTEM


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

    def test_null_fields_fall_back(self):
        service = AIService(api_key="mock_key")
        service._client = MagicMock()
        service._client.models.generate_content.return_value.text = '{"corrected": null, "english": null}'

        res = service.improve_text("Hallo Welt")
        self.assertEqual(res.corrected, "Hallo Welt")
        self.assertEqual(res.english, "")

    def test_missing_key_fails_clearly(self):
        service = AIService(api_key="")
        with self.assertRaisesRegex(ValueError, "API-Schlüssel"):
            service.improve_text("Hallo")

    def test_write_prompt_uses_writer_instructions_as_plain_text(self):
        service = AIService(api_key="mock_key")
        service._client = MagicMock()
        service._client.models.generate_content.return_value.text = "  Überarbeite die Oberfläche der App.\n"

        self.assertEqual(service.write_prompt("mach die app schöner"), "Überarbeite die Oberfläche der App.")
        kwargs = service._client.models.generate_content.call_args.kwargs
        self.assertIn("mach die app schöner", kwargs["contents"])
        self.assertEqual(kwargs["config"].system_instruction, PROMPT_WRITER_SYSTEM)
        self.assertIsNone(kwargs["config"].response_mime_type)

    def test_write_prompt_tries_next_model_on_empty_answer(self):
        service = AIService(api_key="mock_key")
        service._client = MagicMock()
        service._client.models.generate_content.side_effect = [MagicMock(text=""), MagicMock(text="Prompt")]

        self.assertEqual(service.write_prompt("Hallo"), "Prompt")
        self.assertEqual(service._client.models.generate_content.call_count, 2)

    def test_write_prompt_rejects_empty_text(self):
        with self.assertRaises(ValueError):
            AIService(api_key="mock_key").write_prompt("   ")


if __name__ == "__main__":
    unittest.main()

