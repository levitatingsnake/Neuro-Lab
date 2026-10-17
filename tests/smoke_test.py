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

    def test_local_backup_and_restore_controls_are_present_and_scoped(self):
        self.assertIn('id="exportNeuroLabData"', self.html)
        self.assertIn('id="importNeuroLabData"', self.html)
        self.assertIn('backup.format !== "neurolab-backup"', self.html)
        self.assertIn('!allowedKey(key) || typeof value !== "string"', self.html)
        self.assertIn('window.confirm("Restore this backup?', self.html)
        self.assertIn("course-[a-z0-9_-]+", self.html)

    def test_backup_is_inside_mind_training_and_preserves_cycle_settings(self):
        mind_start = self.html.index('id="mindHome"')
        mind_end = self.html.index("</section>", mind_start)
        backup_pos = self.html.index('id="dataBackup"')
        self.assertLess(mind_start, backup_pos)
        self.assertLess(backup_pos, mind_end)
        self.assertIn("cycle-v1", self.html)

    def test_mind_training_saves_practice_followups_and_reflections(self):
        self.assertIn('id="mindPracticeHistory"', self.html)
        self.assertIn("mindState.followUps.push(entry)", self.html)
        self.assertIn("entry.reflection=document.getElementById", self.html)
        self.assertIn("renderMindHistory();if(mindState.step", self.html)

    def test_mind_progress_insights_use_saved_checkin_counts(self):
        self.assertIn('id="mindProgressInsights"', self.html)
        self.assertIn('const counts=entries.reduce', self.html)
        self.assertIn('"Check-ins"', self.html)
        self.assertIn('"Helpful moments"', self.html)
        self.assertIn('"Adjustments"', self.html)
        self.assertIn("Your first check-in will create a baseline.", self.html)

    def test_mind_skills_map_and_missions_are_persistent(self):
        self.assertIn('id="mindSkillsPanel"', self.html)
        self.assertIn('id="mindSkillGrid"', self.html)
        self.assertIn('id="mindMissionList"', self.html)
        self.assertIn("const mindSkillCatalog=[", self.html)
        self.assertIn("const mindMissionCatalog=[", self.html)
        self.assertIn("mindState.completedMissions=current.filter", self.html)
        self.assertIn("saveMind();renderMindSkills()", self.html)
        self.assertIn("renderMindHistory();renderMindSkills();", self.html)

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
