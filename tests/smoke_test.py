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
        self.assertIn("body.world-picker-mode .shell>:not(.top):not(#worldLanding){display:none!important}", self.html)
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

    def test_backup_controls_are_available_and_preserve_cycle_settings(self):
        mind_start = self.html.index('id="mindHome"')
        mind_end = self.html.index("</section>", mind_start)
        backup_pos = self.html.index('id="dataBackup"')
        self.assertLess(mind_start, mind_end)
        self.assertGreater(backup_pos, mind_end)
        backup_end = self.html.index("</section>", backup_pos)
        backup = self.html[backup_pos:backup_end]
        self.assertIn('id="exportNeuroLabData"', backup)
        self.assertIn('id="importNeuroLabData"', backup)
        self.assertIn("cycle-v1", self.html)

    def test_mind_training_saves_practice_followups_and_reflections(self):
        self.assertIn('id="mindPracticeHistory"', self.html)
        self.assertIn("mindState.followUps.push(entry)", self.html)
        self.assertIn("entry.reflection=document.getElementById", self.html)
        self.assertIn("mindState.followUps=mindState.followUps.slice(-100)", self.html)
        self.assertIn('replies.innerHTML=\'<div class="field"><label for="mindFollowUpNote">', self.html)

    def test_saved_mind_conversation_is_restored_on_reload(self):
        self.assertIn("function restoreMindConversation()", self.html)
        self.assertIn("mindState.messages.slice(-30).forEach(message=>", self.html)
        self.assertIn("mindBubble(\"user\",String(message.label||mindQuestions[message.step].choices.find", self.html)
        self.assertIn("function initMind(){restoreMindConversation();renderMindHistory();renderMindSkills();", self.html)

    def test_mind_progress_insights_use_recent_checkins_and_reflection_count(self):
        self.assertIn('const recent=entries.slice(-3)', self.html)
        self.assertRegex(self.html, r'\brecentTotal\s*=\s*recent\.length')
        self.assertIn('label:"Reflections",value:String(reflectionCount)', self.html)
        self.assertIn('Your recent check-ins more often say the step helped.', self.html)
        self.assertIn('Your recent check-ins show friction or difficulty.', self.html)
        self.assertIn('A few check-ins are clues, not a verdict.', self.html)

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
        self.assertIn('if(!done){if(!current.includes(mission.id))current.push(mission.id)', self.html)
        self.assertNotIn('else{mindState.completedMissions=current.filter', self.html)
        self.assertIn("saveMind();renderMindSkills()", self.html)
        self.assertIn("renderMindHistory();renderMindSkills();", self.html)

    def test_saving_a_mission_reflection_does_not_uncomplete_mission(self):
        start = self.html.find('button.textContent=done?"Save reflection":"Save reflection & complete mission"')
        self.assertGreaterEqual(start, 0)
        end = self.html.find('card.append(meta,title,desc,prompt,reflection,saved,button)', start)
        handler = self.html[start:end]
        self.assertIn('mindState.missionReflections[mission.id]=reflection.value.trim()', handler)
        self.assertIn('if(!done){if(!current.includes(mission.id))current.push(mission.id)', handler)
        self.assertNotIn('else{mindState.completedMissions=current.filter', handler)
        self.assertNotIn('delete mindState.missionCompletedAt[mission.id]', handler)

    def test_mind_plan_adapts_to_latest_checkin(self):
        self.assertIn('const latest=Array.isArray(mindState.followUps)?mindState.followUps[mindState.followUps.length-1]:null;', self.html)
        self.assertIn('latest.outcome==="hard"', self.html)
        self.assertIn('latest.outcome==="missed"', self.html)
        self.assertIn('latest.outcome==="helped"', self.html)
        self.assertIn('latest.outcome==="changed"', self.html)
        self.assertIn('Link the smallest possible version to something you already do.', self.html)
        self.assertIn('Make the experiment smaller: spend just 30 seconds', self.html)

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
        self.assertIn("const tarotLayouts=", self.html)
        self.assertIn('pattern="Several "+dominantSuit[0]+" cards recur, bringing "', self.html)
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
        self.assertIn('const CACHE = "neurolab-shell-v46"', worker)
        self.assertIn('if (url.origin !== self.location.origin) return;', worker)
        self.assertIn('event.request.mode === "navigate"', worker)
        self.assertIn('let the request fail normally instead of substituting HTML for that asset', worker)

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


    def test_alchemy_formula_planner_behaviour(self):
        alchemy = (ROOT / "alchemy.html").read_text(encoding="utf-8")
        start = alchemy.index("function materialProfile")
        end = alchemy.index("function syncEngineOptions", start)
        engine_functions = alchemy[start:end]
        harness = """
const $ = () => ({});
let last = null, workingState = null, workingFingerprint = null, operationHistory = [], formulaNote = "";
function hash(s){let h=2166136261;for(let i=0;i<s.length;i++){h^=s.charCodeAt(i);h=Math.imul(h,16777619)}return (h>>>0).toString(16).padStart(8,"0")}
""" + engine_functions + """
const raw = "Light and dark meet in the garden. Fire changes water, while earth holds the signal. I want to understand the pattern and integrate opposites.";
const profileCheck = materialProfile("Alpha beta gamma. Delta epsilon.");
if (profileCheck.sentences.length !== 2) throw Error("Sentence parser must preserve two sentences");
if (Math.abs(profileCheck.averageSentenceLength - 2.5) > 1e-9) throw Error("Word-count parser must measure whitespace-delimited words");
const outcomes = ["clarity","release","integrate","possibilities","embody","full"];
for (const outcome of outcomes) {
  const plan = planFormula(raw, outcome, "balanced", "make the pattern clearer");
  if (!plan.sequence.length || !plan.alternatives.length) throw Error("Missing plan for " + outcome);
  if (plan.alternatives.length !== Math.min(5, plan.candidateCount)) throw Error("Unexpected shortlist size for " + outcome);\n  if (plan.candidateCount < (outcome === "full" ? 1 : 6)) throw Error("Planner did not expand operation orderings for " + outcome);
  if (plan.sequence.length > 4) throw Error("Adaptive search exceeded its four-operation bound");
  if (!plan.reason || !plan.method || !Number.isInteger(plan.candidateCount)) throw Error("Planner omitted its selection rationale or search metadata");
  if (outcome !== "full" && !plan.alternatives.some(x => x.sequence.length === 4)) throw Error("Planner did not explore inserted operations for " + outcome);
  const best = Math.min(...plan.alternatives.map(x => {
    let state = materialProfile(raw).state.slice();
    for (const rite of x.sequence) state = transformAlchemy(raw, rite, "balanced", "make the pattern clearer", state).after;
    return Math.sqrt(state.reduce((sum, value, i) => sum + Math.pow(value - plan.target[i], 2), 0) / state.length);
  }));
  if (Math.abs(best - plan.distance) > 1e-9) throw Error("Planner did not select the minimum-distance candidate for " + outcome);
  let state = materialProfile(raw).state.slice();
  for (const rite of plan.sequence) {
    const result = transformAlchemy(raw, rite, "balanced", "make the pattern clearer", state);
    if (result.after.length !== 10 || result.after.some(v => !Number.isFinite(v) || v < 0 || v > 1)) throw Error("Invalid state after " + rite);
    state = result.after;
  }
  const finalDistance = Math.sqrt(state.reduce((sum, value, i) => sum + Math.pow(value - plan.target[i], 2), 0) / state.length);
  if (Math.abs(finalDistance - plan.distance) > 1e-9) throw Error("Reported final distance differs from executing selected formula for " + outcome);
  if (Math.abs(plan.score - (1 - plan.distance)) > 1e-9) throw Error("Reported heuristic fit is inconsistent for " + outcome);
  const repeat = planFormula(raw, outcome, "balanced", "make the pattern clearer");
  if (JSON.stringify(plan.sequence) !== JSON.stringify(repeat.sequence)) throw Error("Planner is not deterministic for " + outcome);
}
console.log("PASS: six outcomes, candidate minimisation, bounded state, deterministic selection");
"""
        with tempfile.NamedTemporaryFile("w", suffix=".js", encoding="utf-8") as temp:
            temp.write(harness)
            temp.flush()
            result = subprocess.run(["node", temp.name], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, f"Alchemy behavioural test failed:\\n{result.stdout}\\n{result.stderr}")
        self.assertIn("PASS: six outcomes", result.stdout)

    def test_alchemy_formula_run_records_each_executed_step(self):
        alchemy = (ROOT / "alchemy.html").read_text(encoding="utf-8")
        engine_start = alchemy.index("function materialProfile")
        engine_end = alchemy.index("function syncEngineOptions", engine_start)
        engine_functions = alchemy[engine_start:engine_end]
        summary_start = alchemy.index("function summary()")
        summary_end = alchemy.index("function planFormula", summary_start)
        summary_function = alchemy[summary_start:summary_end]
        harness = """
const elements = {
  engine: {value:"alchemy"}, outcome:{value:"clarity"}, intensity:{value:"balanced"},
  intention:{value:"clarify"}, material:{value:"Light and dark meet. Fire changes water and earth holds the signal."},
  rite:{value:"transmute"}
};
const $ = id => elements[id] || (elements[id] = {value:"", textContent:"", classList:{add(){},remove(){}}});
const $console = {textContent:""};
let last = null, workingState = null, workingFingerprint = null, operationHistory = [];
function hash(s){let h=2166136261;for(let i=0;i<s.length;i++){h^=s.charCodeAt(i);h=Math.imul(h,16777619)}return (h>>>0).toString(16).padStart(8,"0")}
function render(){}
function transmute(){
  const raw=$("material").value.trim(), rite=$("rite").value, intensity=$("intensity").value, intention=$("intention").value;
  const result=transformAlchemy(raw,rite,intensity,intention,workingState);
  workingState=result.after.slice();
  operationHistory.push({step:operationHistory.length+1,rite,intensity,intention,before:result.before.slice(),after:result.after.slice(),trace:result.trace.map(x=>({name:x.name,detail:x.detail}))});
  last={engine:{type:"local symbolic transformation engine"},inputFingerprint:hash(raw),settings:{rite,intensity},operations:result.trace,transformation:{dimensions:result.after.map((v,i)=>({label:"dimension "+i,before:result.before[i],after:v}))}};
}
""" + engine_functions + """
function render(){}
""" + summary_function + """
runFormula();
if (!last || !last.formula) throw Error("Formula result was not recorded");
if (last.formula.steps.length !== last.formula.sequence.length) throw Error("Step trace length differs from executed formula");
for (let i=0;i<last.formula.steps.length;i++) {
  const step=last.formula.steps[i], entry=operationHistory[i];
  if (step.rite !== entry.rite || step.step !== i+1) throw Error("Step trace does not match actual operation history");
  if (Math.abs(step.beforeDistance-step.afterDistance-step.improvement)>0.00011) throw Error("Step improvement metric is inconsistent");
}
const report=summary();
if (!report.includes("Step 1 (") || !report.includes("Selected formula:")) throw Error("Copied summary omits the executed formula trace");
console.log("PASS: executed formula steps, per-step metrics and copied summary agree");
"""
        with tempfile.NamedTemporaryFile("w", suffix=".js", encoding="utf-8") as temp:
            temp.write(harness)
            temp.flush()
            result = subprocess.run(["node", temp.name], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, f"Formula-run integration test failed:\n{result.stdout}\n{result.stderr}")
        self.assertIn("PASS: executed formula steps", result.stdout)

    def test_alchemy_manual_operations_evolve_state_and_new_material_resets_it(self):
        alchemy = (ROOT / "alchemy.html").read_text(encoding="utf-8")
        transmute_start = alchemy.index("function transmute(){const raw")
        transmute_end = alchemy.index("function esc(s)", transmute_start)
        transmute_function = alchemy[transmute_start:transmute_end]
        profile_start = alchemy.index("function materialProfile")
        profile_end = alchemy.index("function transformAlchemy", profile_start)
        profile_function = alchemy[profile_start:profile_end]
        transform_start = profile_end
        transform_end = alchemy.index("function render()", transform_start)
        transform_function = alchemy[transform_start:transform_end]
        harness = """
const elements = {
  material:{value:"Fire and water. A signal emerges from the dark."},
  engine:{value:"alchemy"}, rite:{value:"dissolution"}, intensity:{value:"balanced"},
  intention:{value:"test continuity"}, output:{classList:{add(){},remove(){}},scrollIntoView(){}}
};
const $ = id => elements[id] || (elements[id]={value:"",textContent:"",classList:{add(){},remove(){},toggle(){}}});
const $console={textContent:"",appendChild(){}};
const document={createElement(){return {textContent:"",className:""}},querySelectorAll(){return [{classList:{toggle(){}}},{classList:{toggle(){}}}]}};
function matchMedia(){return {matches:true}}
function hash(s){let h=2166136261;for(let i=0;i<s.length;i++){h^=s.charCodeAt(i);h=Math.imul(h,16777619)}return (h>>>0).toString(16).padStart(8,"0")}
function resetConsole(){$console.textContent=""}
function log(s){$console.textContent += s+"\\n"}
function render(){}
let last=null,workingState=null,workingFingerprint=null,operationHistory=[];
""" + profile_function + transform_function + transmute_function + """
const seedOne=materialProfile(elements.material.value).state.slice();
transmute();
if(operationHistory.length!==1) throw Error("First manual operation was not recorded");
if(JSON.stringify(operationHistory[0].before)!==JSON.stringify(seedOne)) throw Error("First operation did not start from seed");
const afterOne=workingState.slice();
elements.rite.value="coagulation";
transmute();
if(operationHistory.length!==2) throw Error("Second operation was not appended to the bench history");
if(JSON.stringify(operationHistory[1].before)!==JSON.stringify(afterOne)) throw Error("Second operation did not start from the prior result");
elements.material.value="A completely different pattern: earth, structure and weight.";
const seedTwo=materialProfile(elements.material.value).state.slice();
elements.rite.value="separation";
transmute();
if(operationHistory.length!==1) throw Error("Changing material failed to start a fresh operation history");
if(JSON.stringify(operationHistory[0].before)!==JSON.stringify(seedTwo)) throw Error("New material reused the previous material's transformed state");
if(workingFingerprint!==hash(elements.material.value)) throw Error("New material fingerprint was not updated");
if(last.input!==elements.material.value) throw Error("Result record does not match the new material");
console.log("PASS: operations evolve bench state and material changes reset the experiment");
"""
        with tempfile.NamedTemporaryFile("w", suffix=".js", encoding="utf-8") as temp:
            temp.write(harness)
            temp.flush()
            result = subprocess.run(["node", temp.name], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, f"Bench continuity integration test failed:\\n{result.stdout}\\n{result.stderr}")
        self.assertIn("PASS: operations evolve bench state", result.stdout)

    def test_alchemy_reset_restores_seed_and_clears_run_state(self):
        alchemy = (ROOT / "alchemy.html").read_text(encoding="utf-8")
        handler_start = alchemy.index('$("resetState").onclick=()=>{')
        handler_end = alchemy.index('$("example").onclick=', handler_start)
        reset_handler = alchemy[handler_start:handler_end]
        profile_start = alchemy.index("function materialProfile")
        profile_end = alchemy.index("function transformAlchemy", profile_start)
        profile_function = alchemy[profile_start:profile_end]
        harness = """
const elements = {
  material:{value:"Fire and water. A signal emerges from the dark."},
  output:{classList:{add(name){this.hidden=true},remove(){this.hidden=false}}},
  console:{textContent:"old result"}, resetState:{}, rite:{value:"rubedo"}
};
const $ = id => elements[id] || (elements[id]={value:"",textContent:"",classList:{add(){},remove(){}}});
const $console = elements.console;
const document = {querySelectorAll(){return [{classList:{remove(){}}},{classList:{remove(){}}}]}};
let last={old:true}, workingState=[0.1,0.2], workingFingerprint="old", operationHistory=[{rite:"rubedo"}];
function hash(s){let h=2166136261;for(let i=0;i<s.length;i++){h^=s.charCodeAt(i);h=Math.imul(h,16777619)}return (h>>>0).toString(16).padStart(8,"0")}
""" + profile_function + """
""" + reset_handler + """
elements.resetState.onclick();
if(last!==null) throw Error("Reset did not clear the previous result");
if(operationHistory.length!==0) throw Error("Reset did not clear operation history");
if(workingFingerprint!==hash(elements.material.value.trim())) throw Error("Reset fingerprint does not match current material");
if(JSON.stringify(workingState)!==JSON.stringify(materialProfile(elements.material.value.trim()).state)) throw Error("Reset did not restore the material seed profile");
if(!elements.output.classList.hidden) throw Error("Reset did not hide the old output");
if(!elements.console.textContent.includes("BENCH RESET")) throw Error("Reset status message missing");
elements.material.value="x";
elements.resetState.onclick();
if(!elements.console.textContent.includes("Enter material before resetting")) throw Error("Short-material guard missing");
console.log("PASS: reset restores seed, clears history/result and guards empty material");
"""
        with tempfile.NamedTemporaryFile("w", suffix=".js", encoding="utf-8") as temp:
            temp.write(harness)
            temp.flush()
            result = subprocess.run(["node", temp.name], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, f"Bench reset integration test failed:\\n{result.stdout}\\n{result.stderr}")
        self.assertIn("PASS: reset restores seed", result.stdout)

    def test_alchemy_export_serializes_the_full_record(self):
        alchemy = (ROOT / "alchemy.html").read_text(encoding="utf-8")
        export_start = alchemy.index("function exportRecord()")
        export_end = alchemy.index("function summary()", export_start)
        export_function = alchemy[export_start:export_end]
        harness = """
let last={inputFingerprint:"abc123",formula:{name:"Clarify the signal",sequence:["separation","distillation"],steps:[{step:1,rite:"separation"}]}};
let blobPayload=null, clicked=false, revoked=null, scheduled=null;
class Blob { constructor(parts,options){blobPayload={text:parts.join(""),type:options.type}} }
const URL={createObjectURL(){return "blob:test"},revokeObjectURL(url){revoked=url}};
const document={createElement(tag){if(tag!=="a")throw Error("Expected download link");return {href:"",download:"",click(){clicked=true}}}};
function setTimeout(fn,ms){scheduled={fn,ms};return 1}
""" + export_function + """
exportRecord();
if(!clicked) throw Error("Export did not trigger a download");
if(!blobPayload||blobPayload.type!=="application/json") throw Error("Export did not create a JSON blob");
const exported=JSON.parse(blobPayload.text);
if(exported.formula.steps[0].rite!=="separation") throw Error("Export omitted the executed formula trace");
if(!exported.formula.sequence.includes("distillation")) throw Error("Export omitted the selected sequence");
if(scheduled.ms!==1000) throw Error("Export URL cleanup was not scheduled");
scheduled.fn();
if(revoked!=="blob:test") throw Error("Export URL was not revoked");
last=null;clicked=false;exportRecord();
if(clicked) throw Error("Export should do nothing when there is no result");
console.log("PASS: export downloads complete JSON including formula trace and cleans up URL");
"""
        with tempfile.NamedTemporaryFile("w", suffix=".js", encoding="utf-8") as temp:
            temp.write(harness)
            temp.flush()
            result = subprocess.run(["node", temp.name], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, f"JSON export integration test failed:\\n{result.stdout}\\n{result.stderr}")
        self.assertIn("PASS: export downloads complete JSON", result.stdout)

    def test_alchemy_reports_use_real_line_breaks(self):
        alchemy = (ROOT / "alchemy.html").read_text(encoding="utf-8")
        summary_start = alchemy.index("function summary()")
        summary_end = alchemy.index("function planFormula", summary_start)
        summary = alchemy[summary_start:summary_end]
        run_start = alchemy.index("function runFormula()")
        run_end = alchemy.index("function syncEngineOptions", run_start)
        run_formula = alchemy[run_start:run_end]
        self.assertNotIn(r"\\n", summary, "Copied/exported summaries must contain real line breaks, not literal backslash-n text")
        self.assertNotIn(r"\\n", run_formula, "Formula progress and completion messages must contain real line breaks")

    def test_veil_digital_alchemy_is_linked_local_and_syntax_valid(self):
        alchemy = (ROOT / "alchemy.html").read_text(encoding="utf-8")
        veil = (ROOT / "veil.html").read_text(encoding="utf-8")
        self.assertIn('href="./alchemy.html"', veil)
        self.assertIn("VEIL DIGITAL ALCHEMY // OPERATIVE LAB 004", alchemy)
        self.assertIn("function transmute()", alchemy)
        self.assertIn("function transformAlchemy", alchemy)
        self.assertIn("function materialProfile", alchemy)
        self.assertIn("function runFormula()", alchemy)
        self.assertIn("function planFormula", alchemy)
        self.assertIn("target-state fit", alchemy)
        self.assertIn("Alternative sequences compared", alchemy)
        self.assertIn("Heuristic fit, not a probability", alchemy)
        self.assertIn("distanceToGoal", alchemy)
        self.assertIn("moved closer to the target profile", alchemy)
        self.assertIn("moved farther from the target profile", alchemy)
        self.assertIn("Actual result:", alchemy)
        self.assertIn("last.formula.startDistance", alchemy)
        self.assertIn("last.formula.finalDistance", alchemy)
        self.assertIn("steps:stepAssessments", alchemy)
        self.assertIn("Step-by-step fit:", alchemy)
        self.assertIn("last.formula.steps.map", alchemy)
        render_start = alchemy.index("function render()")
        formula_note = alchemy.index("const formulaNote=last.formula?", render_start)
        quantum_branch = alchemy.index('if(last.engine.type==="classical state-vector simulation")', render_start)
        self.assertLess(formula_note, quantum_branch, "Formula note must be initialized before either renderer branch")
        self.assertIn("Clarify the signal", alchemy)
        self.assertIn("Loosen a fixed pattern", alchemy)
        self.assertIn("Integrate opposites", alchemy)
        self.assertIn("Generate possibilities", alchemy)
        self.assertIn("Stabilise a result", alchemy)
        self.assertIn("operationHistory.push", alchemy)
        self.assertIn("Choose the outcome you want", alchemy)
        self.assertIn("workingState=result.after.slice()", alchemy)
        self.assertIn("operationHistory.push", alchemy)
        self.assertIn("id=\"resetState\"", alchemy)
        self.assertIn("Sequence on this bench", alchemy)
        self.assertIn("function transformAlchemy(raw,rite,intensity,intention,startingState=null)", alchemy)
        self.assertIn("Choose the outcome you want and run its recommended formula", alchemy)
        self.assertNotIn("look for echoes in your local VEIL field", alchemy)
        self.assertIn("Calcination · burn away excess", alchemy)
        self.assertIn("Fermentation · generate new forms", alchemy)
        self.assertIn("Alchemical transmutation", alchemy)
        self.assertIn("Quantum state-vector experiment", alchemy)
        self.assertIn("intention", alchemy)
        self.assertIn("function hadamard", alchemy)
        self.assertIn("function controlledPhase", alchemy)
        self.assertIn("function diffusion", alchemy)
        self.assertIn("function probabilities", alchemy)
        self.assertIn("state-vector simulation", alchemy)
        self.assertIn("State integrity", alchemy)
        self.assertIn("deterministic pseudorandom sample", alchemy)
        self.assertIn('id="rite"', alchemy)
        self.assertIn('id="intensity"', alchemy)
        self.assertNotIn("localStorage.getItem", alchemy)
        self.assertNotIn("function notes()", alchemy)
        self.assertIn("function links(){const a=d.observations", veil)
        self.assertIn("rarityScore", veil)
        self.assertIn("gapDays", veil)
        self.assertIn("Time separation:", veil)
        self.assertIn("Evidence to inspect:", veil)
        self.assertIn("rarer shared terms:", veil)
        self.assertIn("cross=!same&&(terms.length>0||shared.length>0)", veil)
        self.assertIn('id="savedThreads"', veil)
        self.assertIn("data-pin=", veil)
        self.assertIn("data-pinstatus=", veil)
        self.assertIn("SAME DATE", veil)
        self.assertIn("rarer shared words", veil)
        self.assertIn("function exportRecord()", alchemy)
        self.assertIn("Your text is not transmitted by this page.", alchemy)
        self.assertIn("not a physical or supernatural transmutation", alchemy)
        for page_name, page in (("veil.html", veil), ("alchemy.html", alchemy)):
            scripts = re.findall(r"<script\b[^>]*>(.*?)</script\s*>", page, flags=re.I | re.S)
            self.assertTrue(scripts, f"No inline scripts found in {page_name}")
            for index, script in enumerate(scripts, start=1):
                if not script.strip():
                    continue
                with tempfile.NamedTemporaryFile("w", suffix=".js", encoding="utf-8") as temp:
                    temp.write(script)
                    temp.flush()
                    result = subprocess.run(["node", "--check", temp.name], capture_output=True, text=True)
                self.assertEqual(result.returncode, 0, f"{page_name} inline script {index} has a syntax error:\n{result.stderr}")


if __name__ == "__main__":
    unittest.main(verbosity=2)
