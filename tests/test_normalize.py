import unittest

from collector.normalize import normalize_wasalt_listing


class NormalizeWasaltListingTests(unittest.TestCase):
    def test_keeps_property_facts_and_excludes_contact_information(self):
        record = normalize_wasalt_listing(
            {
                "source_url": "https://wasalt.sa/en/property/sale/example-5935070",
                "title": "Villa 228 SQM Facing East on 12m Width Street",
                "location": "Al-Muhammadiyah, North Riyadh, Riyadh",
                "price_text": "4,690,000",
                "area_text": "228 SQM",
                "bedrooms_text": "5 bedrooms",
                "description": "Villa for Sale in Al-Muhammadiyah, Riyadh",
                "contact_name": "A broker name",
                "phone": "+966555555555",
            },
            captured_at="2026-11-18T12:00:00Z",
        )

        self.assertEqual(record["source"], "wasalt")
        self.assertEqual(record["price"], 4690000)
        self.assertEqual(record["currency"], "SAR")
        self.assertEqual(record["area_sqm"], 228.0)
        self.assertEqual(record["bedrooms"], 5)
        self.assertEqual(record["city"], "Riyadh")
        self.assertNotIn("contact_name", record)
        self.assertNotIn("phone", record)


if __name__ == "__main__":
    unittest.main()
