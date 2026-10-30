import unittest
from src.hotkey_service import parse_hotkey


class TestParseHotkey(unittest.TestCase):
    def test_modifiers_and_keys(self):
        self.assertEqual(parse_hotkey("<ctrl>+<alt>+<space>"), (0x2 | 0x1, 0x20))
        self.assertEqual(parse_hotkey("<ctrl>+<shift>+q"), (0x2 | 0x4, ord("Q")))
        self.assertEqual(parse_hotkey("<ctrl>+<F12>"), (0x2, 0x7B))
        self.assertEqual(parse_hotkey("<pause>"), (0, 0x13))

    def test_invalid(self):
        for bad in ("<ctrl>+<alt>", "<ctrl>+ä", "<ctrl>+<f25>", "<strg>+s"):
            with self.assertRaises(ValueError):
                parse_hotkey(bad)


if __name__ == "__main__":
    unittest.main()
