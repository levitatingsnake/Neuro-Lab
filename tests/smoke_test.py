from pathlib import Path
import re
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
HTML_PATH = ROOT / "index.html"


class NeuroLabSmokeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.html = HTML_PATH.read_text(encoding="utf-8")

    def test_inner_cosmos_has_four_distinct_hub_options(self):
        tabs = re.findall(r'<button[^>]*class="cosmos-tab[^"]*"[^>]*data-cosmos="([^"]+)"[^>]*>(.*?)</button>', self.html)
        labels = {key: re.sub(r"<[^>]+>", "", label).replace("&amp;", "&").strip() for key, label in tabs}
        self.assertEqual(set(labels), {"stars", "cycle", "library", "mind"})
        self.assertIn("Birth chart", labels["stars"])
        self.assertIn("Cycle", labels["cycle"])
        self.assertIn("Wisdom library", labels["library"])
        self.assertIn("Mind Training", labels["mind"])

    def test_mind_training_has_a_dedicated_panel_and_route(self):
        self.assertIn('id="mindHome"', self.html)
        self.assertIn('if(view==="mind"){openMindTraining();return}', self.html)
        self.assertIn('function openMindTraining()', self.html)

    def test_mind_training_is_not_nested_inside_wisdom_library(self):
        start = self.html.index('id="cosmosLibrary"')
        end = self.html.index('id="cosmosCycle"', start)
        self.assertNotIn("mind-training-library-entry", self.html[start:end])

    def test_returning_to_inner_cosmos_resets_the_selected_tab(self):
        self.assertIn('x.dataset.cosmos==="stars"', self.html)
        self.assertIn('$("cosmosStars")?.classList.remove("hidden")', self.html)

    def test_inline_javascript_parses(self):
        scripts = re.findall(r"<script\b[^>]*>(.*?)</script\s*>", self.html, flags=re.I | re.S)
        self.assertTrue(scripts, "No inline scripts found")
        node = subprocess.run(["node", "--version"], capture_output=True, text=True)
        self.assertEqual(node.returncode, 0, "Node.js is required for inline JavaScript syntax checks")
        for index, script in enumerate(scripts, start=1):
            if not script.strip():
                continue
            with tempfile.NamedTemporaryFile("w", suffix=".js", encoding="utf-8") as temp:
                temp.write(script)
                temp.flush()
                result = subprocess.run(["node", "--check", temp.name], capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, f"Inline script {index} has a syntax error:\n{result.stderr}")


if __name__ == "__main__":
    unittest.main(verbosity=2)
