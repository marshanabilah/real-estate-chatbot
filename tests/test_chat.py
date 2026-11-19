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
        self.assertEqual(len(response["matches"]), 1)
        self.assertEqual(response["matches"][0]["title"], "Neptune, Interiors by Mouawad")
        self.assertEqual(response["matches"][0]["property_type"], "villa")
        self.assertNotIn("description", response["matches"][0])

    def test_applies_property_bedroom_and_price_constraints_from_question(self):
        response = answer_question(
            "Show me villas in Riyadh with at least 4 bedrooms under SAR 4 million",
            load_records(),
            api_key=None,
        )

        self.assertEqual(len(response["sources"]), 3)
        self.assertTrue(all(source["source"] == "wasalt" for source in response["sources"]))
        self.assertIn("Villa 210 SQM", response["answer"])
        self.assertNotIn("Floor with 4 Bedrooms", response["answer"])
        self.assertTrue(all(item["property_type"] == "villa" for item in response["matches"]))
        self.assertTrue(all(item["price"] <= 4_000_000 for item in response["matches"]))


if __name__ == "__main__":
    unittest.main()
