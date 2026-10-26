import json
import pathlib
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
COMPENDIUM = ROOT / "compendium"

class TestCompendiumOracle(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.archive = json.loads((COMPENDIUM / "sources.json").read_text(encoding="utf-8"))
        cls.schools = json.loads((COMPENDIUM / "oracle-schools.json").read_text(encoding="utf-8"))
        cls.oracle_html = (ROOT / "oracle/index.html").read_text(encoding="utf-8")
        cls.index_html = (ROOT / "index.html").read_text(encoding="utf-8")
        cls.worker = (ROOT / "service-worker.js").read_text(encoding="utf-8")

    def test_archive_has_50_metadata_records(self):
        items = self.archive["items"]
        self.assertEqual(len(items), 50)
        self.assertEqual(len({entry["id"] for entry in items}), 50)
        self.assertTrue(all(entry.get("source_url", "").startswith("https://") for entry in items))
        self.assertTrue(all(entry.get("full_text_included") is False for entry in items))

    def test_four_thinkers_six_topics(self):
        expected = {"Crowley", "Gurdjieff", "Osho", "Krishnamurti"}
        self.assertEqual(len(self.schools["figures"]), 4)
        self.assertEqual(len(self.schools["topic_views"]), 6)
        for topic, views in self.schools["topic_views"].items():
            self.assertEqual(set(views), expected, topic)
            for view in views.values():
                self.assertTrue(view["prompt"] and view["action"] and view["caveat"])

    def test_rights_and_source_links(self):
        self.assertTrue(all(src["reuse"] == "link_metadata_only_pending_rights" for src in self.schools["source_catalog"]))
        self.assertTrue(all(src["full_text_included"] is False for src in self.schools["source_catalog"]))
        self.assertTrue(all(src["url"].startswith("https://") for src in self.schools["source_catalog"]))

    def test_oracle_navigation(self):
        self.assertIn('href="./oracle/"', self.index_html)
        self.assertIn("../compendium/sources.json", self.oracle_html)
        self.assertIn("../compendium/oracle-schools.json", self.oracle_html)
        self.assertIn("source-grounded", self.oracle_html.lower())
        self.assertIn("./oracle/index.html", self.worker)
        self.assertIn("./compendium/oracle-schools.json", self.worker)

    def test_local_reflection_without_external_ai(self):
        self.assertIn("localStorage.setItem", self.oracle_html)
        self.assertIn("neurolab-oracle-journal-v1", self.oracle_html)
        self.assertNotIn("innerHTML", self.oracle_html)
        self.assertNotIn("api.openai.com", self.oracle_html)

if __name__ == "__main__":
    unittest.main()
