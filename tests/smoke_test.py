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

    def test_world_picker_shows_only_world_choices_and_keeps_intro_copy(self):
        self.assertIn("body.world-picker-mode #innerCosmos,body.world-picker-mode #outerCosmos,body.world-picker-mode #mindHome{display:none!important}", self.html)
        landing_start = self.html.index('id="worldLanding"')
        landing_end = self.html.index("</section>", landing_start)
        landing = self.html[landing_start:landing_end]
        self.assertIn("NEURO//LAB · TWO WORLDS, ONE UNIVERSE", landing)
        self.assertIn("Turn inward to explore the mind, meaning and human wisdom.", landing)
        self.assertIn("Turn outward to explore our star, the space around Earth, and the science of a changing universe.", landing)
        self.assertEqual(len(re.findall(r'class="world-choice"', landing)), 2)
        self.assertIn('</section>\n\n<section id="outerCosmos"', self.html)

    def test_inner_cosmos_has_four_distinct_hub_options(self):
        tabs = re.findall(r'<button[^>]*class="cosmos-tab[^"]*"[^>]*data-cosmos="([^"]+)"[^>]*>(.*?)</button>', self.html)
        labels = {key: re.sub(r"<[^>]+>", "", label).replace("&amp;", "&").strip() for key, label in tabs}
        self.assertEqual(set(labels), {"stars", "cycle", "library", "mind", "tarot"})
        self.assertIn("Birth chart", labels["stars"])
        self.assertIn("Cycle", labels["cycle"])
        self.assertIn("Wisdom library", labels["library"])
        self.assertIn("Mind Training", labels["mind"])
        self.assertIn("Tarot", labels["tarot"])

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

    def test_mind_missions_save_reflections_and_recommend_next_step(self):
        self.assertIn('id="mindNextRecommendation"', self.html)
        self.assertIn("Your reflection (optional)", self.html)
        self.assertIn('className="mind-mission-reflection"', self.html)
        self.assertIn("mindState.missionReflections[mission.id]=reflection.value.trim()", self.html)
        self.assertIn("mindState.missionCompletedAt[mission.id]=new Date().toISOString()", self.html)
        self.assertIn('latest.outcome==="hard"||latest.outcome==="missed"', self.html)
        self.assertIn('latest.outcome==="helped"', self.html)
        self.assertIn("SUGGESTED NEXT STEP", self.html)

    def test_outer_cosmos_uses_refreshing_nasa_solar_images(self):
        self.assertIn('id="liveSunImage"', self.html)
        self.assertIn('data-sun-channel="0171"', self.html)
        self.assertIn('data-sun-channel="0193"', self.html)
        self.assertIn('data-sun-channel="0304"', self.html)
        self.assertIn('data-sun-channel="HMII"', self.html)
        self.assertIn("https://sdo.gsfc.nasa.gov/assets/img/latest/latest_1024_", self.html)
        self.assertIn("15*60*1000", self.html)
        self.assertIn('id="sunArtisticToggle"', self.html)
        self.assertIn("loadLiveSun(activeSunChannel);if(typeof window.neuroLabLoadSpaceWeather", self.html)
        self.assertIn("NASA SOLAR DYNAMICS OBSERVATORY", self.html)

    def test_saved_tarot_reader_scroll_syntax_is_valid(self):
        self.assertIn('block:"start"});const btn=$("saveTarotReading")', self.html)
        self.assertNotIn('block:"start");const btn=$("saveTarotReading")', self.html)

    def test_tarot_uses_original_svg_artwork_and_refined_layout(self):
        self.assertIn("function tarotCardArtwork(card,deckInfo,reversed)", self.html)
        self.assertIn('class="tarot-card-artwork"', self.html)
        self.assertIn('class="tarot-spread-stage"', self.html)
        self.assertIn('class="tarot-interpretation-list"', self.html)
        self.assertIn(".tarot-card-spread.spread-10 .tarot-card-entry:nth-child(2)", self.html)
        self.assertIn("@media(max-width:700px)", self.html)

    def test_tarot_reader_lives_in_inner_cosmos_with_random_spreads(self):
        self.assertIn('id="cosmosTarot"', self.html)
        self.assertIn('data-cosmos="tarot"', self.html)
        self.assertIn('id="tarotQuestion"', self.html)
        self.assertIn('id="tarotDeck"', self.html)
        self.assertIn('id="tarotSpread"', self.html)
        self.assertIn('id="drawTarot"', self.html)
        self.assertIn('id="tarotDrawAgain"', self.html)
        self.assertIn('id="replayTarotReveal"', self.html)
        self.assertIn("function replayTarotReveal()", self.html)
        self.assertIn('class="tarot-reveal-status" aria-live="polite"', self.html)
        self.assertIn("function shuffleTarot(deck)", self.html)
        self.assertIn("shuffleTarot(buildTarotDeck()).slice(0,count)", self.html)
        self.assertIn("function tarotCardReading", self.html)
        self.assertIn("WEAVING THE CARDS TOGETHER", self.html)
        self.assertIn("@keyframes tarot-reveal", self.html)
        self.assertIn("prefers-reduced-motion:reduce", self.html)
        self.assertIn("Egyptian-inspired mythic lens", self.html)
        self.assertIn("Thoth tradition", self.html)
        for spread in ('value="4"', 'value="6"', 'value="7"', 'value="9"', 'value="12"'):
            self.assertIn(spread, self.html)
        self.assertIn("const tarotLayouts=", self.html)
        self.assertIn("function tarotRandomInt(max)", self.html)
        self.assertIn("window.crypto.getRandomValues", self.html)
        self.assertIn("function tarotSynthesisText(", self.html)
        self.assertIn("dominantSuit", self.html)
        self.assertIn('pattern="Several "+dominantSuit[0]+" cards recur, bringing "', self.html)
        self.assertIn("12:[[2,1],[3,1],[4,1],[5,2],[5,3],[5,4],[4,5],[3,5],[2,5],[1,4],[1,3],[1,2]]", self.html)
        self.assertIn("7:[[1,3],[1,2],[2,1],[3,1],[4,2],[4,3],[2,3]]", self.html)
        self.assertIn("spreadIntros", self.html)
        self.assertIn("spread-12", self.html)
        self.assertIn("@keyframes tarot-console-scan", self.html)
        self.assertIn("@keyframes tarot-button-sweep", self.html)

    def test_tarot_saved_archive_is_local_and_included_in_backup(self):
        self.assertIn('id="tarotSavedList"', self.html)
        self.assertIn('id="saveTarotReading"', self.html)
        self.assertIn("function loadSavedTarot()", self.html)
        self.assertIn("function saveTarotSnapshot()", self.html)
        self.assertIn("function openSavedTarot(id)", self.html)
        self.assertIn("function deleteSavedTarot(id)", self.html)
        self.assertIn('localStorage.setItem("neurolab-tarot-saved-v1"', self.html)
        self.assertIn("tarot-saved-v1|report-date", self.html)
        self.assertIn("saved.slice(0,10)", self.html)

    def test_world_navigation_fallback_and_cache_refresh(self):
        self.assertIn("Last-resort world navigation", self.html)
        self.assertIn('target.closest(".world-choice[data-world]")', self.html)
        self.assertIn('target.closest("#closeCosmos")', self.html)
        worker = (ROOT / "service-worker.js").read_text(encoding="utf-8")
        self.assertIn('const CACHE = "neurolab-shell-v44"', worker)

    def test_outer_cosmos_has_mission_control_navigation(self):
        self.assertIn('id="outerMissionControl"', self.html)
        self.assertIn('data-observatory-target="cosmosSun"', self.html)
        self.assertIn('data-observatory-target="solarOrbitPanel"', self.html)
        self.assertIn('data-observatory-target="auroraPanel"', self.html)
        self.assertIn('data-observatory-target="spaceDataGrid"', self.html)
        self.assertIn('id="liveSunImage"', self.html)

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
