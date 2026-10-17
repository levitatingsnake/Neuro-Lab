import assert from "node:assert/strict";
import { readFileSync, existsSync } from "node:fs";
import vm from "node:vm";

const html = readFileSync(new URL("../index.html", import.meta.url), "utf8");
const serviceWorker = readFileSync(new URL("../service-worker.js", import.meta.url), "utf8");
const manifest = JSON.parse(readFileSync(new URL("../manifest.json", import.meta.url), "utf8"));

const coreTabs = [
  ["stars", /data-cosmos="stars"[^>]*>[\s\S]*?Birth chart/i],
  ["cycle", /data-cosmos="cycle"[^>]*>[\s\S]*?Cycle &amp; wellbeing/i],
  ["library", /data-cosmos="library"[^>]*>[\s\S]*?Wisdom library/i],
  ["mind", /data-cosmos="mind"[^>]*>[\s\S]*?Mind Training/i],
];

for (const [name, pattern] of coreTabs) {
  assert.match(html, pattern, `Missing or misplaced core Inner Cosmos tab: ${name}`);
}
assert.match(html, /data-cosmos="tarot"[^>]*>[\s\S]*?Tarot/i, "Tarot entry should remain available");
assert.match(html, /data-world="inner"/, "Inner Cosmos world entry is missing");
assert.match(html, /data-world="outer"/, "Outer Cosmos world entry is missing");
assert.match(html, /id="cosmosMind"/, "Mind Training content container is missing");
assert.match(html, /id="cosmosLibrary"/, "Wisdom Library content container is missing");
assert.match(html, /navigator\.serviceWorker\.register\("\.\/service-worker\.js"\)/, "Service worker registration is missing");

for (const match of html.matchAll(/<script\b([^>]*)>([\s\S]*?)<\/script\s*>/gi)) {
  if (/\bsrc\s*=/.test(match[1]) || !match[2].trim()) continue;
  new vm.Script(match[2], { filename: "index.html:inline-script" });
}

for (const asset of ["./", "./index.html", "./manifest.json", "./icon.svg", "./astronomy.browser.min.js"]) {
  assert.ok(serviceWorker.includes(JSON.stringify(asset)), `Service worker cache list is missing ${asset}`);
  const localPath = asset === "./" ? "../index.html" : `../${asset.slice(2)}`;
  assert.ok(existsSync(new URL(localPath, import.meta.url)), `Referenced local asset is missing: ${asset}`);
}

assert.equal(manifest.short_name, "NEURO//LAB", "PWA short name changed unexpectedly");
console.log("NEURO//LAB smoke checks passed: navigation, mind training, tarot, inline JS syntax, and PWA assets.");
