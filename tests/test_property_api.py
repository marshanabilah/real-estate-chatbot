import unittest
from unittest.mock import patch

from fastapi.testclient import TestClient

from app.main import app


class PropertyApiTests(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

    def test_filters_listings_by_city_type_bedrooms_and_price(self):
        response = self.client.get(
            "/api/properties",
            params={
                "city": "Riyadh",
                "propertyType": "villa",
                "minBedrooms": 4,
                "maxPrice": 4_000_000,
            },
        )

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload["total"], 3)
        self.assertTrue(all(item["property_type"] == "villa" for item in payload["items"]))
        self.assertTrue(all(item["source_url"] for item in payload["items"]))

    def test_serves_the_property_discovery_page(self):
        response = self.client.get("/")

        self.assertEqual(response.status_code, 200)
        self.assertIn("Property discovery", response.text)
        self.assertIn("Search the catalog", response.text)

    def test_sets_baseline_security_headers(self):
        response = self.client.get("/api/health")

        self.assertEqual(response.headers["x-content-type-options"], "nosniff")
        self.assertEqual(response.headers["x-frame-options"], "DENY")
        self.assertIn("default-src 'self'", response.headers["content-security-policy"])

    def test_returns_grounded_chat_answer_and_citations(self):
        with patch.dict("os.environ", {"OPENROUTER_API_KEY": ""}, clear=False):
            response = self.client.post("/api/chat", json={"question": "Tell me about Neptune in Riyadh"})

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload["mode"], "retrieval")
        self.assertIn("Neptune", payload["answer"])
        self.assertEqual(payload["sources"][0]["source"], "darglobal")


if __name__ == "__main__":
    unittest.main()
