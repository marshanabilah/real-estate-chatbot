import unittest

from app.catalog import load_records
from app.chat import answer_question


class ChatAnswerTests(unittest.TestCase):
    def test_returns_grounded_fallback_with_source_citation_when_no_model_key(self):
        response = answer_question(
            "Tell me about Neptune in Riyadh",
            load_records(),
            api_key=None,
        )

        self.assertIn("Neptune", response["answer"])
        self.assertEqual(response["mode"], "retrieval")
        self.assertEqual(response["sources"][0]["title"], "Neptune, Interiors by Mouawad")
        self.assertTrue(response["sources"][0]["source_url"].startswith("https://"))
        self.assertEqual(len(response["sources"]), 1)


if __name__ == "__main__":
    unittest.main()
