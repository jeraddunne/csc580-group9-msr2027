import { html, useData, useState, useMemo, Loaded } from "../lib/ui.js";
import { resultsTable } from "../lib/data.js";
import { num } from "../lib/csv.js";
import {
  irr,
  kappaFromTable,
  kappaWords,
  mannWhitney,
  percent,
  precision,
  similarityDetail,
  wilsonCI,
} from "../lib/formulas.js";
import { compileRules, scanText } from "../lib/rules.js";
import { LINKS, QUESTION } from "../content/project.js";

const GROUPS = [
  { title: "Understand the project", ids: ["project", "pipeline", "rules"] },
  { title: "How the numbers are made", ids: ["prevalence", "similarity", "reach", "regression", "holm", "validation", "sensitivity"] },
  { title: "Do it yourself", ids: ["environments", "git", "safety", "glossary"] },
];

const LESSONS = {
  project: { title: "The project in five minutes", kicker: "Start here", blurb: "What a skill is, why copying one can be risky, and our three questions." },
  pipeline: { title: "How the pipeline works", kicker: "Big picture", blurb: "From the dataset to the report, one stage at a time." },
  rules: { title: "Risk rules, and a rule tester", kicker: "Try it", blurb: "What a rule is, what severity means, and a box to test text against the real rules." },
  prevalence: { title: "How common: shares and confidence", kicker: "RQ1", blurb: "Why 8.9% comes with a range, and how the range is worked out." },
  similarity: { title: "How alike are two skills", kicker: "RQ3 · Try it", blurb: "Word chunks and the Jaccard similarity, with two boxes to compare." },
  reach: { title: "Do risky skills spread more", kicker: "RQ2 · Try it", blurb: "Comparing two groups when most skills have one copy: ranks, U, and effect size." },
  regression: { title: "Taking other causes into account", kicker: "RQ2", blurb: "The regression, and what an incidence rate ratio of 1.41 means." },
  holm: { title: "Many tests at once", kicker: "RQ2", blurb: "Why four categories that look significant are not, after the Holm adjustment." },
  validation: { title: "Checking the checker", kicker: "Validation · Try it", blurb: "Precision, rater agreement (kappa), and the labelling plan." },
  sensitivity: { title: "Are the results solid", kicker: "Robustness", blurb: "The same analysis under six different choices." },
  environments: { title: "Test environments: how they were made, how to make one", kicker: "Hands on", blurb: "Windows double-click files, Docker, Linux, and GitHub's own computers." },
  git: { title: "How GitHub fits together", kicker: "Plain words", blurb: "Issues, branches, pull requests, reviews, and what this guide does for you." },
  safety: { title: "Working safely and honestly", kicker: "Rules", blurb: "The few rules that protect people, the data, and our grade." },
  glossary: { title: "Glossary", kicker: "Words", blurb: "Every term used in the project, in one line each." },
};

export function Learn({ topic }) {
  if (!topic)
    return html`<section class="page-head"><p class="eyebrow">Plain words, diagrams, and worked examples</p><h1>Learn the project</h1>
        <p class="lede">Each lesson takes five to ten minutes. The examples use the same formulas as our pipeline, checked by tests against the Python code, and the numbers come from the results committed in the project.</p></section>
      ${GROUPS.map((g) => html`<section class="stack" style="gap:10px"><h2>${g.title}</h2><div class="lessons">
        ${g.ids.map((id) => html`<a class="lesson-card" href=${`#/learn/${id}`}><span class="k">${LESSONS[id].kicker}</span><h3>${LESSONS[id].title}</h3><p class="small">${LESSONS[id].blurb}</p></a>`)}
      </div></section>`)}`;
  const L = LESSONS[topic];
  const Body = BODIES[topic];
  if (!L || !Body) return html`<div class="note warn">No lesson called “${topic}”. <a href="#/learn">All lessons</a>.</div>`;
  const order = GROUPS.flatMap((g) => g.ids);
  const i = order.indexOf(topic);
  const next = order[i + 1];
  const prev = order[i - 1];
  return html`<p class="crumbs"><a href="#/learn">Learn</a> / ${L.title}</p>
    <article class="lesson"><header class="page-head"><p class="eyebrow">${L.kicker}</p><h1>${L.title}</h1></header><${Body} /></article>
    <nav class="row between" aria-label="Lessons">${prev ? html`<a class="btn" href=${`#/learn/${prev}`}>← ${LESSONS[prev].title}</a>` : html`<span></span>`}
      ${next ? html`<a class="btn primary" href=${`#/learn/${next}`}>${LESSONS[next].title} →</a>` : html`<a class="btn primary" href="#/">Back home</a>`}</nav>`;
}

const Where = ({ items }) => html`<div class="note small"><b>Where it lives in the project</b>${items.map(([label, path]) => html`<span>${label}: <a href=${LINKS.file(path.split(" ")[0])} target="_blank" rel="noopener"><code>${path}</code></a></span>`)}</div>`;
const Unvalidated = () => html`<div class="note warn small"><b>Preliminary and unvalidated.</b><span>These counts are keyword signals, not confirmed capabilities. They become findings only after the labelled samples are scored (due Oct 27).</span></div>`;
const f2 = (x, d = 2) => (Number.isFinite(x) ? x.toFixed(d) : "n/a");
const Table = ({ name, children }) => {
  const state = useData(`results-${name}`, () => resultsTable(name));
  return html`<${Loaded} state=${state} what=${`Loading ${name}`}>${children}<//>`;
};
function Arrow({ id }) {
  return html`<defs><marker id=${id} viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" class="arrowhead" /></marker></defs>`;
}

// ---- Diagrams --------------------------------------------------------------------------------
function CopyDiagram() {
  const repo = (x, y, label, risky) => html`<g><rect class=${risky ? "box-h" : "box"} x=${x} y=${y} width="150" height="46" rx="6" />
    <text class="tb" x=${x + 12} y=${y + 20} style="font-size:12px">${label}</text><text class="tm" x=${x + 12} y=${y + 36}>SKILL.md${risky ? " + 1 risky line" : ""}</text></g>`;
  return html`<figure><div class="diagram-wrap"><svg class="diagram" viewBox="0 0 760 210" role="img" aria-label="One skill is copied from an original repository into three others; one copy is edited and gains a risky instruction." style="min-width:560px">
    <${Arrow} id="ar-copy" />
    ${repo(20, 82, "Original repo", false)}
    ${repo(300, 12, "Copy in repo B", false)}
    ${repo(300, 82, "Copy in repo C", false)}
    ${repo(300, 152, "Edited copy in D", true)}
    ${repo(580, 152, "Copy of D in E", true)}
    <path class="edge" d="M170,105 C230,105 240,35 298,35" marker-end="url(#ar-copy)" />
    <line class="edge" x1="170" y1="105" x2="298" y2="105" marker-end="url(#ar-copy)" />
    <path class="edge" d="M170,105 C230,105 240,175 298,175" marker-end="url(#ar-copy)" />
    <line class="edge" x1="450" y1="175" x2="578" y2="175" marker-end="url(#ar-copy)" />
    <text class="tl" x="220" y="96">copied</text><text class="tl" x="486" y="166">copied again</text>
  </svg></div><figcaption>Skills spread by copying folders. RQ2 asks whether skills with a risky line are copied more; RQ3 asks whether edits along the way add or remove risky lines (the blue boxes).</figcaption></figure>`;
}

function PipelineDiagram() {
  return html`<figure><div class="diagram-wrap"><svg class="diagram" viewBox="0 0 980 330" role="img" aria-label="Pipeline: the GitSkills sample is filtered to 12,965 skills, scanned by 19 rules, and feeds RQ1 prevalence, RQ2 reach, and RQ3 drift, which are then checked by human validation." style="min-width:820px">
    <${Arrow} id="ar-pipe" />
    <rect class="box" x="10" y="120" width="160" height="96" rx="6" /><text class="tb" x="24" y="146">GitSkills sample</text><text class="t" x="24" y="168">13,000 distinct skills</text><text class="t" x="24" y="186">29,786 copies</text><text class="tm" x="24" y="205">July 2026 snapshot</text>
    <rect class="box" x="206" y="120" width="160" height="96" rx="6" /><text class="tb" x="220" y="146">Population filter</text><text class="t" x="220" y="168">drop 35 symlink stubs</text><text class="t" x="220" y="186">12,965 skills kept</text><text class="tm" x="220" y="205">population_flow.csv</text>
    <rect class="box-a" x="402" y="104" width="200" height="128" rx="6" /><text class="tb" x="416" y="130">Rule scanner</text><text class="t" x="416" y="152">19 rules, 11 risk categories</text><text class="t" x="416" y="170">SKILL.md text and</text><text class="t" x="416" y="188">5,153 bundled scripts</text><text class="tm" x="416" y="210">reads text, never runs it</text>
    <rect class="box-h" x="646" y="20" width="160" height="74" rx="6" /><text class="tb" x="660" y="46">RQ1 Prevalence</text><text class="t" x="660" y="67">share flagged, per</text><text class="t" x="660" y="84">category</text>
    <rect class="box-h" x="646" y="131" width="160" height="74" rx="6" /><text class="tb" x="660" y="157">RQ2 Reach</text><text class="t" x="660" y="178">copies and repos,</text><text class="t" x="660" y="195">flagged vs not</text>
    <rect class="box-h" x="646" y="242" width="160" height="74" rx="6" /><text class="tb" x="660" y="268">RQ3 Drift</text><text class="t" x="660" y="289">variant pairs that</text><text class="t" x="660" y="306">gain or lose a flag</text>
    <rect class="box-d" x="842" y="94" width="130" height="148" rx="6" /><text class="tb" x="854" y="120">Human</text><text class="tb" x="854" y="138">validation</text><text class="t" x="854" y="162">147 signal items</text><text class="t" x="854" y="180">58 lineage pairs</text><text class="t" x="854" y="198">18 drift pairs</text><text class="tm" x="854" y="222">precision, kappa</text>
    <line class="edge" x1="170" y1="168" x2="204" y2="168" marker-end="url(#ar-pipe)" /><line class="edge" x1="366" y1="168" x2="400" y2="168" marker-end="url(#ar-pipe)" />
    <path class="edge" d="M602,140 C624,140 624,57 644,57" marker-end="url(#ar-pipe)" /><line class="edge" x1="602" y1="168" x2="644" y2="168" marker-end="url(#ar-pipe)" /><path class="edge" d="M602,196 C624,196 624,279 644,279" marker-end="url(#ar-pipe)" />
    <text class="tl" x="623" y="160" text-anchor="middle">flags</text>
    <path class="edge" d="M806,57 C826,57 822,130 840,130" marker-end="url(#ar-pipe)" /><line class="edge" x1="806" y1="168" x2="840" y2="168" marker-end="url(#ar-pipe)" /><path class="edge" d="M806,279 C826,279 822,206 840,206" marker-end="url(#ar-pipe)" />
    <text class="tl" x="844" y="84">labelled samples</text><text class="tl" x="646" y="234">pairs with similarity ≥ 0.5</text>
  </svg></div><figcaption>One command, <code>make pipeline</code>, runs every box except human validation, which is people labelling samples.</figcaption></figure>`;
}

function GitDiagram() {
  const box = (x, label, sub, cls = "box") => html`<g><rect class=${cls} x=${x} y="40" width="150" height="62" rx="6" /><text class="tb" x=${x + 12} y="66" style="font-size:13px">${label}</text><text class="tm" x=${x + 12} y="86">${sub}</text></g>`;
  return html`<figure><div class="diagram-wrap"><svg class="diagram" viewBox="0 0 900 150" role="img" aria-label="Issue, then branch, then pull request, then review, then merge into main." style="min-width:700px">
    <${Arrow} id="ar-git" />
    ${box(10, "Issue", "the task")}${box(190, "Branch", "a private copy")}${box(370, "Pull request", "“please add this”", "box-a")}${box(550, "Review", "a teammate checks")}${box(730, "Merge", "into main")}
    ${[160, 340, 520, 700].map((x) => html`<line class="edge" x1=${x} y1="71" x2=${x + 28} y2="71" marker-end="url(#ar-git)" />`)}
    <text class="tl" x="10" y="130">you or the guide</text><text class="tl" x="190" y="130">the guide makes it</text><text class="tl" x="370" y="130">the guide opens it</text><text class="tl" x="550" y="130">not the author</text><text class="tl" x="730" y="130">Product Owner</text>
  </svg></div><figcaption>Every change to the project follows this path, so nothing reaches the approved version (<code>main</code>) without a second person.</figcaption></figure>`;
}

function EnvDiagram() {
  const env = (y, label, sub) => html`<g><rect class="box" x="10" y=${y} width="250" height="50" rx="6" /><text class="tb" x="24" y=${y + 22} style="font-size:13px">${label}</text><text class="tm" x="24" y=${y + 40}>${sub}</text></g>`;
  return html`<figure><div class="diagram-wrap"><svg class="diagram" viewBox="0 0 760 290" role="img" aria-label="Four environments run the same pipeline and are compared with the committed results." style="min-width:600px">
    <${Arrow} id="ar-env" />
    ${env(10, "Windows double-click files", "windows/1-set-up.bat, 2-run-pipeline.bat")}
    ${env(80, "Docker container", "Dockerfile + docker/check.sh")}
    ${env(150, "Linux, following the README", "make setup / data / test / pipeline")}
    ${env(220, "GitHub's computers", "Actions > Container check")}
    <rect class="box-a" x="340" y="95" width="170" height="90" rx="6" /><text class="tb" x="354" y="122">Same pipeline</text><text class="t" x="354" y="144">python -m msr_pipeline</text><text class="t" x="354" y="162">analyze</text>
    <rect class="box-h" x="570" y="95" width="180" height="90" rx="6" /><text class="tb" x="584" y="122">Compare with</text><text class="tb" x="584" y="140">results/</text><text class="tm" x="584" y="162">fresh_run_check.py</text>
    ${[35, 105, 175, 245].map((y) => html`<path class="edge" d=${`M260,${y} C300,${y} 300,140 338,140`} marker-end="url(#ar-env)" />`)}
    <line class="edge" x1="510" y1="140" x2="568" y2="140" marker-end="url(#ar-env)" />
  </svg></div><figcaption>Four different computers, one pipeline, one comparison. If all four match the committed results, the numbers do not depend on anyone's laptop.</figcaption></figure>`;
}

// ---- Lessons -----------------------------------------------------------------------------------
function Project() {
  return html`
    <section><h2>What a skill is</h2>
      <p>AI coding assistants (Claude Code, GitHub Copilot, Cursor and others) can follow <b>skills</b>: a folder with a file called <code>SKILL.md</code> that tells the assistant how to do a job, such as “set up this project” or “deploy the website”. Some skills bring small scripts along. The assistant follows the skill with the developer's own permissions: it can run commands, read files, and reach the internet.</p></section>
    <section><h2>Why copying one can be risky</h2>
      <p>There is no app store or review for skills. People copy the folder from one project to another. A copied skill can carry instructions like “download this script and run it” or “read the API keys”, and nobody checks. Most of the time this is harmless and useful; sometimes it is not.</p>
      <${CopyDiagram} /></section>
    <section><h2>Our question, in plain words</h2>
      <p class="small muted">The exact wording, from RESEARCH_QUESTION.md:</p><blockquote class="note">${QUESTION}</blockquote>
      <ol><li><b>RQ1, how common:</b> what share of skills contain instructions or scripts for risky things, in each of 11 risk categories?</li>
        <li><b>RQ2, do they spread more:</b> are skills with a risky signal copied into more projects than skills without one, even after taking other reasons into account?</li>
        <li><b>RQ3, do copies change:</b> when someone copies a skill and edits it, do the edits add or remove risky instructions?</li></ol></section>
    <section><h2>The data</h2>
      <p>The <b>GitSkills</b> dataset from the MSR 2027 Mining Challenge collected skills from public GitHub projects in July 2026. We use its official sample: <b>13,000 different skill texts</b>, found <b>29,786 times</b> across projects (because of copying). We never run anything from it; we only read the text.</p></section>
    <section><h2>What the first run shows</h2><${Unvalidated} />
      <ul><li><b>RQ1:</b> 8.9% of skills (1,159 of 12,965) have at least one high-risk signal. <a href="#/learn/prevalence">How that is worked out</a>.</li>
        <li><b>RQ2:</b> flagged skills get about 1.4 times as many extra copies as otherwise similar skills. <a href="#/learn/regression">What that means</a>.</li>
        <li><b>RQ3:</b> of 245 look-alike skill pairs, only 1 both differs in a risky category and has dates to show which came first. Too few to say which way risk moves. <a href="#/learn/similarity">How pairs are found</a>.</li></ul></section>
    <section><h2>What we do not claim</h2>
      <ul><li>A keyword is not a capability: a skill may mention <code>rm -rf</code> to warn against it. That is why people label samples (<a href="#/learn/validation">checking the checker</a>).</li>
        <li>Flagged is not malicious.</li><li>“Copied more” is an association, not proof that risky lines cause copying.</li></ul></section>`;
}

function Pipeline() {
  const stages = [
    ["Load", "Reads the sample database, read only.", "src/msr_pipeline/load.py", "nothing yet"],
    ["Filter", "Keeps real skill text; drops 35 one-line “symlink stubs” that are just a path.", "src/msr_pipeline/skill_risk.py (is_symlink_stub)", "results/population_flow.csv"],
    ["Scan", "Runs 19 text rules over each SKILL.md and 5,153 bundled script files.", "src/msr_pipeline/skill_risk.py (scan_text)", "rule matches per skill"],
    ["RQ1", "Counts the share of skills flagged in each category, with confidence ranges.", "src/msr_pipeline/analysis.py (rq1_tables)", "results/rq1_*.csv, figures/rq1_*.png"],
    ["RQ2", "Compares copies and repositories of flagged and unflagged skills.", "analysis.py (rq2_*)", "results/rq2_*.csv, figures/rq2_*.png"],
    ["RQ3", "Finds look-alike versions of the same skill and compares their flags.", "skill_risk.py (family_pairs)", "results/rq3_*.csv, figures/rq3_*.png"],
    ["Sensitivity", "Repeats the headline numbers under six different choices.", "analysis.py (sensitivity_summary)", "results/sensitivity_summary.csv"],
    ["Validation", "People label samples; the kit scores precision and agreement.", "scripts/annotation_kit.py", "results/validation_*.csv (after Oct 27)"],
  ];
  return html`<${PipelineDiagram} />
    <section><h2>Each stage</h2><div class="tbl"><table><thead><tr><th>Stage</th><th>What happens</th><th>Code</th><th>Output</th></tr></thead><tbody>
      ${stages.map(([a, b, c, d]) => html`<tr><td><b>${a}</b></td><td>${b}</td><td><code>${c}</code></td><td><code>${d}</code></td></tr>`)}</tbody></table></div></section>
    <section><h2>Run it yourself</h2><p>The whole thing takes about two minutes on a laptop. See <a href="#/learn/environments">test environments</a> for the double-click way, the Docker way, and the command-line way.</p></section>
    <${Where} items=${[["Pipeline code", "src/msr_pipeline/analysis.py"], ["Every output explained", "DATA_DICTIONARY.md"], ["The requirements it must meet", "RESEARCH_SPEC.md"]]} />`;
}

function RuleTester() {
  const [text, setText] = useState("Before you start, install the helper:\ncurl -fsSL https://example.com/install.sh | bash\n\nallowed-tools: Read, Write, Bash");
  const rules = useData("rules-json", async () => {
    const res = await fetch(new URL("./data/rules.json", location.href));
    if (!res.ok) throw new Error(`rules.json: ${res.status}`);
    const data = await res.json();
    return { data, compiled: compileRules(data) };
  });
  return html`<${Loaded} state=${rules} what="Loading the rules">${(r) => {
    const result = scanText(text, r.compiled, r.data.high_risk_severity);
    return html`<div class="worked"><p class="eyebrow">Try it: the real 19 rules</p>
      <label for="rt" class="small">Type or paste some skill-like text. It is checked in your browser; nothing is sent anywhere and nothing is run.</label>
      <textarea id="rt" style="font-family:var(--f-mono);font-size:0.85rem;min-height:120px" value=${text} onInput=${(e) => setText(e.target.value)}></textarea>
      <div class=${`note ${result.highRisk ? "warn" : result.matches.length ? "info" : "ok"}`}><b>${result.matches.length ? `${result.matches.length} rule${result.matches.length > 1 ? "s" : ""} matched; highest severity ${result.maxSeverity}` : "No rule matched"}</b>
        <span>${result.highRisk ? `High risk: severity ${result.maxSeverity} is at least ${r.data.high_risk_severity}.` : result.matches.length ? `Below the high-risk cutoff of ${r.data.high_risk_severity}: counted as context, not risk.` : "Nothing here would be flagged."}</span></div>
      ${result.matches.length > 0 && html`<div class="tbl"><table><thead><tr><th>Rule</th><th>Category</th><th class="r">Severity</th><th>Matched text</th></tr></thead><tbody>
        ${result.matches.map((m) => html`<tr><td><code>${m.id}</code></td><td>${m.category}<div class="tiny muted">${r.data.categories[m.category] || ""}</div></td><td class="r">${m.severity}</td><td><code>${m.excerpt}</code></td></tr>`)}</tbody></table></div>`}
      <details><summary class="small">All ${r.data.rules.length} rules with their examples</summary><div class="tbl"><table><thead><tr><th>Rule</th><th class="r">Sev.</th><th>Matches</th><th>Does not match</th></tr></thead><tbody>
        ${r.data.rules.map((x) => html`<tr><td><code>${x.id}</code><div class="tiny muted">${x.category}</div></td><td class="r">${x.severity}</td><td class="small">${x.match.map((s) => html`<div><code>${s}</code></div>`)}</td><td class="small">${x.no_match.map((s) => html`<div><code>${s}</code></div>`)}</td></tr>`)}</tbody></table></div></details>
    </div>`;
  }}<//>`;
}

function Rules() {
  return html`
    <section><h2>What a rule is</h2>
      <p>A rule is a text pattern plus a label. For example, rule <code>R-RCE-001</code> looks for <code>curl</code> or <code>wget</code> followed on the same line by a pipe into a shell, like <code>curl https://… | bash</code>. That line downloads a script and runs it at once, with no chance to read it first.</p>
      <p>Each rule has a <b>category</b> (one of 11 kinds of risk, such as remote code, credentials, or destructive operations) and a <b>severity</b> from 1 (informational) to 10 (a direct path to harm). A skill is <b>high risk</b> when any rule with severity <b>6 or more</b> matches.</p>
      <p>Some rules are context only. “This skill runs shell commands” (<code>SHELL</code>, severity 3) matches a third of all skills; it describes what a skill does, not a risk.</p></section>
    <section><h2>Why rules can be wrong</h2>
      <ul><li><b>False alarm:</b> the text mentions the pattern to warn against it, or in an example.</li>
        <li><b>Miss:</b> a risky instruction phrased in a way no pattern covers.</li></ul>
      <p>That is why every rule's precision is measured by people labelling a sample (<a href="#/learn/validation">checking the checker</a>). Each rule also carries its own examples, and the tests fail if a rule stops matching them.</p></section>
    <${RuleTester} />
    <${Where} items=${[["The rules", "rules/skill_risk_rules.yaml"], ["The scanner", "src/msr_pipeline/skill_risk.py"], ["What each category means", "docs/research/THREAT_MODEL.md"]]} />`;
}

function Prevalence() {
  const [k, setK] = useState(1159);
  const [n, setN] = useState(12965);
  const [lo, hi] = wilsonCI(k, n);
  return html`<${Unvalidated} />
    <section><h2>The share</h2><p>A share is simply how many out of how many: skills flagged ÷ all skills.</p>
      <div class="formula">share = flagged ÷ total = 1,159 ÷ 12,965 = 0.0894 = 8.9%</div></section>
    <section><h2>Why it comes with a range</h2>
      <p>Our 12,965 skills are a sample of a much larger set. A different sample would give a slightly different share. The <b>95% confidence interval</b> is the range of shares that fits our sample well. We use the <b>Wilson</b> interval, which behaves well even when the share is small or the sample is small.</p>
      <div class="formula">centre = (p + z²/2n) / (1 + z²/n)      half-width = z·√(p(1−p)/n + z²/4n²) / (1 + z²/n)      z = 1.96</div>
      <p class="small muted">p is the share, n the number of skills. The interval is centre ± half-width.</p></section>
    <div class="worked"><p class="eyebrow">Try it</p>
      <div class="fields"><div class="field"><label for="wk">Flagged</label><input id="wk" type="number" min="0" value=${k} onInput=${(e) => setK(Math.max(0, +e.target.value))} /></div>
        <div class="field"><label for="wn">Total</label><input id="wn" type="number" min="1" value=${n} onInput=${(e) => setN(Math.max(1, +e.target.value))} /></div></div>
      <dl class="kv"><dt>Share</dt><dd>${percent(k / n, 2)}</dd><dt>95% interval</dt><dd>${percent(lo, 2)} to ${percent(hi, 2)}</dd><dt>Width</dt><dd>${percent(hi - lo, 2)}</dd></dl>
      <p class="small">Try 116 of 1,297 (a sample ten times smaller): same share, a range about three times wider. Bigger samples give narrower ranges.</p></div>
    <section><h2>Two ways to count</h2><p>A skill copied 50 times can be counted once (<b>distinct</b>) or 50 times (<b>copy-weighted</b>). RQ1 reports both. When they differ a lot, the category is concentrated in heavily copied skills.</p>
      <${Table} name="rq1_prevalence_by_category.csv">${(rows) => html`<div class="tbl"><table><thead><tr><th>Category</th><th class="r">Distinct share</th><th class="r">95% interval</th><th class="r">Copy-weighted share</th></tr></thead><tbody>
        ${rows.filter((r) => num(r.high_risk_contents) > 0).map((r) => html`<tr><td>${r.category}</td><td class="r">${percent(num(r.high_risk_share), 2)}</td><td class="r">${percent(num(r.high_risk_ci_low), 2)}–${percent(num(r.high_risk_ci_high), 2)}</td><td class="r">${percent(num(r.high_risk_occurrence_share), 2)}</td></tr>`)}</tbody></table></div>`}<//></section>
    <${Where} items=${[["Wilson interval", "src/msr_pipeline/analysis.py"], ["The table above", "results/rq1_prevalence_by_category.csv"]]} />`;
}

function Similarity() {
  const [a, setA] = useState("Run the install script to set up the tool. Then open the config file and add your project name before you start the server.");
  const [b, setB] = useState("Run the install script to set up the tool. Then open the config file and add your team name before you start the local server.");
  const d = useMemo(() => similarityDetail(a, b), [a, b]);
  return html`
    <section><h2>The idea</h2><p>To find versions of the same skill, we cut each text into overlapping <b>5-word chunks</b> (“shingles”) and ask what share of all the chunks the two texts have in common. That share is the <b>Jaccard similarity</b>: 1 means identical, 0 means nothing in common.</p>
      <div class="formula">similarity = chunks in both ÷ chunks in either</div>
      <p>Words are lower-cased and punctuation is ignored, so “Run the install” and “run the INSTALL!” match. Changing one word breaks the five chunks that contain it, so small edits lower the score a little and rewrites lower it a lot.</p></section>
    <div class="worked"><p class="eyebrow">Try it</p>
      <div class="grid two"><div class="field"><label for="sa">Text A</label><textarea id="sa" value=${a} onInput=${(e) => setA(e.target.value)}></textarea></div>
        <div class="field"><label for="sb">Text B</label><textarea id="sb" value=${b} onInput=${(e) => setB(e.target.value)}></textarea></div></div>
      <dl class="kv"><dt>Chunks in A</dt><dd>${d.a.size}</dd><dt>Chunks in B</dt><dd>${d.b.size}</dd><dt>In both</dt><dd>${d.shared.length}</dd><dt>In either</dt><dd>${d.union}</dd>
        <dt>Similarity</dt><dd>${d.shared.length} ÷ ${d.union} = ${f2(d.similarity, 3)} ${d.similarity >= 0.5 ? "(a pair: 0.5 or more)" : "(not a pair: below 0.5)"}</dd></dl>
      <details><summary class="small">Show the chunks (green: in both)</summary><div>${[...d.shared.map((s) => [s, true]), ...d.onlyA.map((s) => [s, false]), ...d.onlyB.map((s) => [s, false])].map(([s, both]) => html`<span class=${`shingle${both ? " both" : ""}`}>${s}</span>`)}</div></details>
      <p class="tiny muted">The pipeline stores each chunk as a number (a CRC32 hash) to save memory; the result is the same.</p></div>
    <section><h2>How pairs are chosen</h2><p>Only skills with the same name in their front matter are compared (a “family”), and a pair counts when its similarity is <b>0.5 or more</b>. For each pair, the older version is <b>a</b> and the newer is <b>b</b> when both have commit dates; then we can see whether the newer one added or dropped a high-risk category.</p>
      <${Table} name="rq3_threshold_sweep.csv">${(rows) => html`<div class="tbl"><table><thead><tr><th class="r">Threshold</th><th class="r">Pairs</th><th class="r">Differ in a risky category</th><th class="r">Dated both sides</th><th class="r">Newer adds</th><th class="r">Newer drops</th></tr></thead><tbody>
        ${rows.map((r) => html`<tr style=${r.threshold === "0.5" ? "font-weight:600" : ""}><td class="r">${r.threshold}</td><td class="r">${r.lineage_pairs}</td><td class="r">${r.differing_pairs}</td><td class="r">${r.ordered_pairs}</td><td class="r">${r.ordered_newer_adds}</td><td class="r">${r.ordered_newer_drops}</td></tr>`)}</tbody></table></div>
        <p class="small">At every threshold, at most one dated pair changes, so RQ3 is reported as case studies, not a trend.</p>`}<//></section>
    <${Where} items=${[["Chunks and similarity", "src/msr_pipeline/skill_risk.py"], ["All pairs at 0.5", "results/rq3_lineage_pairs.csv"]]} />`;
}

function Reach() {
  const [g, setG] = useState("1, 1, 2, 5, 9, 12");
  const [r, setR] = useState("1, 1, 1, 2, 3");
  const parse = (s) => s.split(/[\s,;]+/).map(Number).filter((x) => Number.isFinite(x));
  const G = parse(g);
  const R = parse(r);
  const res = G.length >= 2 && R.length >= 2 ? mannWhitney(G, R) : null;
  return html`<${Unvalidated} />
    <section><h2>The problem with averages here</h2><p>Most skills are copied once; a few are copied over 150 times. With numbers that lopsided, one very popular skill can move an average a lot. So the main test compares <b>ranks</b> instead of raw numbers.</p></section>
    <section><h2>Mann-Whitney U, step by step</h2>
      <ol><li>Put every skill from both groups in one list, sorted by copies, and number them 1, 2, 3… (ties share the average rank).</li>
        <li>Add up the ranks of the flagged group, and subtract the smallest sum it could have had. That is <b>U</b>.</li>
        <li>U is the number of (flagged, unflagged) pairs where the flagged skill has more copies, with ties counting half.</li></ol>
      <div class="formula">U = (sum of flagged ranks) − n₁(n₁+1)/2        effect size r = 2U ÷ (n₁·n₂) − 1</div>
      <p>The <b>rank-biserial</b> effect size r runs from −1 to 1. It is the chance that a random flagged skill has more copies than a random unflagged one, minus the chance of the reverse. 0 means no difference.</p></section>
    <div class="worked"><p class="eyebrow">Try it</p>
      <div class="grid two"><div class="field"><label for="mg">Copies of flagged skills</label><input id="mg" type="text" value=${g} onInput=${(e) => setG(e.target.value)} /></div>
        <div class="field"><label for="mr">Copies of other skills</label><input id="mr" type="text" value=${r} onInput=${(e) => setR(e.target.value)} /></div></div>
      ${res ? html`<div class="tbl"><table><thead><tr><th>Group</th><th>Copies → rank</th></tr></thead><tbody>
          <tr><td>Flagged</td><td>${G.map((x, i) => html`<span class="shingle both">${x} → ${res.ranks[i]}</span>`)}</td></tr>
          <tr><td>Other</td><td>${R.map((x, i) => html`<span class="shingle">${x} → ${res.ranks[G.length + i]}</span>`)}</td></tr></tbody></table></div>
        <dl class="kv"><dt>Sum of flagged ranks</dt><dd>${f2(res.rankSumGroup, 1)}</dd><dt>U</dt><dd>${f2(res.rankSumGroup, 1)} − ${res.n1}·${res.n1 + 1}/2 = ${f2(res.u, 1)}</dd>
          <dt>Effect size r</dt><dd>2·${f2(res.u, 1)} ÷ (${res.n1}·${res.n2}) − 1 = ${f2(res.rankBiserial, 3)}</dd><dt>p-value</dt><dd>${f2(res.p, 3)} ${res.p < 0.05 ? "(below 0.05)" : "(not below 0.05: could easily be chance)"}</dd></dl>`
        : html`<p class="small">Enter at least two numbers in each box.</p>`}
      <p class="tiny muted">Same method as the pipeline (scipy's two-sided test with the normal approximation), checked by the app's tests.</p></div>
    <section><h2>Our numbers</h2><${Table} name="rq2_mannwhitney.csv">${(rows) => html`<div class="tbl"><table><thead><tr><th>Outcome</th><th class="r">Flagged</th><th class="r">Other</th><th class="r">Mean flagged</th><th class="r">Mean other</th><th class="r">p</th><th class="r">Effect r</th></tr></thead><tbody>
        ${rows.map((x) => html`<tr><td>${x.outcome}</td><td class="r">${Number(x.n_group).toLocaleString()}</td><td class="r">${Number(x.n_reference).toLocaleString()}</td><td class="r">${f2(num(x.mean_group))}</td><td class="r">${f2(num(x.mean_reference))}</td><td class="r">${f2(num(x.p_value), 4)}</td><td class="r">${f2(num(x.rank_biserial), 3)}</td></tr>`)}</tbody></table></div>
      <p class="small">The difference is real (small p) but small (r about 0.04): the medians are both 1 copy. A bootstrap, which re-draws the sample 2,000 times, puts the extra copies per flagged skill between 0.12 and 1.25 on average.</p>`}<//></section>
    <${Where} items=${[["The test", "src/msr_pipeline/analysis.py (mann_whitney, rank_biserial)"], ["The table", "results/rq2_mannwhitney.csv"]]} />`;
}

function Regression() {
  const [coef, setCoef] = useState(0.344);
  return html`<${Unvalidated} />
    <section><h2>Why a second method</h2><p>Flagged skills might be copied more for other reasons: they might be longer, live in popular projects, or sit in the standard <code>.claude/skills</code> folder that tools pick up automatically. A <b>regression</b> compares flagged and unflagged skills that are alike in those other ways (“controls”).</p>
      <p>Our controls: text length, bundled scripts, folder location, the project's stars, and its main language.</p></section>
    <section><h2>The model, in plain words</h2><p>The outcome is <b>extra copies</b> (copies − 1). Because it is a count with many zeros and a few huge values, we use a <b>negative binomial</b> model (NB2), made for exactly that. Each factor gets a coefficient; raising e to it gives an <b>incidence rate ratio</b> (IRR): how many times more extra copies, all else equal.</p>
      <div class="formula">IRR = e^coefficient      e^0.3444 = 1.411</div>
      <p>1.41 means a flagged skill gets about <b>41% more extra copies</b> than an otherwise similar skill without a signal. The 95% interval, 1.20 to 1.66, does not include 1 (no difference), so the difference is unlikely to be chance.</p></section>
    <div class="worked"><p class="eyebrow">Try it: coefficient to IRR</p>
      <div class="field"><label for="cf">Coefficient: ${f2(coef, 3)}</label><input id="cf" type="range" min="-1.5" max="2" step="0.01" value=${coef} onInput=${(e) => setCoef(+e.target.value)} /></div>
      <dl class="kv"><dt>IRR</dt><dd>e^${f2(coef, 3)} = ${f2(irr(coef), 3)}</dd><dt>In words</dt><dd>${irr(coef) >= 1 ? `${f2((irr(coef) - 1) * 100, 0)}% more extra copies` : `${f2((1 - irr(coef)) * 100, 0)}% fewer extra copies`}</dd></dl>
      <p class="small">0 gives 1 (no effect); negative coefficients give fewer copies. Try 1.83, the coefficient for the standard skills folder: over six times as many copies.</p></div>
    <section><h2>Every factor in the model</h2><${Table} name="rq2_negbin.csv">${(rows) => html`<div class="tbl"><table><thead><tr><th>Factor</th><th class="r">IRR</th><th class="r">95% interval</th><th class="r">p</th></tr></thead><tbody>
      ${rows.filter((x) => x.term !== "const" && x.term !== "alpha").map((x) => html`<tr style=${x.term === "high_risk" ? "font-weight:600" : ""}><td>${TERM[x.term] || x.term}</td><td class="r">${f2(num(x.irr))}</td><td class="r">${f2(num(x.irr_ci_low))}–${f2(num(x.irr_ci_high))}</td><td class="r">${num(x.p_value) < 0.001 ? "<0.001" : f2(num(x.p_value), 3)}</td></tr>`)}</tbody></table></div>
      <p class="small muted">Each factor is compared with a skill under a <code>skills/</code> folder in a Python project. Where a skill lives matters far more than whether it is flagged.</p>`}<//></section>
    <section><h2>What it does not show</h2><p>A regression shows association, not cause. Something we did not measure (for example, what the skill is for) could explain both. The report says this plainly.</p></section>
    <${Where} items=${[["The model", "src/msr_pipeline/analysis.py (negbin_design, rq2_negbin)"], ["The table", "results/rq2_negbin.csv"]]} />`;
}
const TERM = {
  high_risk: "Has a high-risk signal",
  log1p_body_chars: "Longer text (per unit of log length)",
  has_scripts: "Bundles scripts",
  log1p_stars: "More project stars (per unit of log stars)",
  location_canonical: "In the standard .claude/skills folder",
  location_other: "Somewhere else",
  "language_(none)": "Project has no main language",
  language_HTML: "HTML project",
  language_JavaScript: "JavaScript project",
  language_Rust: "Rust project",
  language_Shell: "Shell project",
  language_TypeScript: "TypeScript project",
  language_Vue: "Vue project",
  language_other: "Another language",
};

function Holm() {
  return html`<section><h2>The problem</h2><p>If you run one test at the usual 5% level, there is a 1 in 20 chance of a false alarm. We run eight tests, one per risk category with enough skills; the chance that at least one false alarm appears is then about 34%. Some “findings” would be luck.</p></section>
    <section><h2>The Holm adjustment</h2><ol><li>Sort the p-values from smallest to largest.</li><li>Multiply the smallest by the number of tests m, the next by m−1, and so on.</li><li>Keep each adjusted value at least as large as the one before it, and at most 1.</li><li>A result counts only if its adjusted p-value is below 0.05.</li></ol>
      <div class="formula">adjusted p(k) = max over j ≤ k of min(1, (m − j + 1) · p(j))</div></section>
    <section><h2>Our category tests</h2><${Table} name="rq2_category_tests.csv">${(rows) => {
      const tested = rows.filter((x) => x.tested === "True").sort((a, b) => num(a.p_value) - num(b.p_value));
      return html`<div class="tbl"><table><thead><tr><th>Category</th><th class="r">Skills</th><th class="r">p alone</th><th class="r">Holm p</th><th>Counts?</th></tr></thead><tbody>
        ${tested.map((x) => html`<tr><td>${x.category}</td><td class="r">${x.contents}</td><td class="r">${f2(num(x.p_value), 3)}${num(x.p_value) < 0.05 ? " *" : ""}</td><td class="r">${f2(num(x.p_holm), 3)}</td><td>${x.significant_holm_05 === "True" ? "yes" : "no"}</td></tr>`)}</tbody></table></div>
        <p class="small">Four categories (marked *) look significant alone; none survive the adjustment. So we do not say any single category drives the reach difference. Categories with too few skills are not tested.</p>`;
    }}<//></section>
    <${Where} items=${[["The adjustment", "src/msr_pipeline/analysis.py (holm_adjust)"], ["The table", "results/rq2_category_tests.csv"]]} />`;
}

function Validation() {
  const [c, setC] = useState({ risky: 12, benign: 5, none: 3 });
  const [t, setT] = useState([[20, 5], [10, 15]]);
  const p = precision(c.risky, c.benign, c.none);
  const k = kappaFromTable(t);
  const setCell = (i, j, v) => setT((x) => x.map((row, a) => row.map((val, b) => (a === i && b === j ? Math.max(0, +v || 0) : val))));
  return html`<section><h2>Why people have to check</h2><p>The scanner finds words, not intentions. So we take a random, stratified sample of flagged items and a person labels each one from a written guideline:</p>
      <ul><li><b>RISKY</b>: the skill really tells the agent to do the risky thing.</li><li><b>BENIGN_CONTEXT</b>: the capability is there but used safely or explained (for example, a documented install step).</li><li><b>NOT_PRESENT</b>: a false match; the capability is not there at all.</li></ul></section>
    <section><h2>Precision</h2><p>Precision is how often a flag is right. We report two versions: <b>strict</b> (only RISKY counts) and <b>capability</b> (RISKY or BENIGN_CONTEXT count, because the capability is real either way).</p>
      <div class="formula">strict = RISKY ÷ all      capability = (RISKY + BENIGN_CONTEXT) ÷ all</div></section>
    <div class="worked"><p class="eyebrow">Try it: precision of one rule</p>
      <div class="fields">${[["risky", "RISKY"], ["benign", "BENIGN_CONTEXT"], ["none", "NOT_PRESENT"]].map(([key, label]) => html`<div class="field"><label for=${key}>${label}</label><input id=${key} type="number" min="0" value=${c[key]} onInput=${(e) => setC((s) => ({ ...s, [key]: Math.max(0, +e.target.value || 0) }))} /></div>`)}</div>
      <dl class="kv"><dt>Strict precision</dt><dd>${c.risky} ÷ ${p.n} = ${percent(p.strict)} (95%: ${percent(p.strictCI[0])}–${percent(p.strictCI[1])})</dd>
        <dt>Capability precision</dt><dd>${c.risky + c.benign} ÷ ${p.n} = ${percent(p.capability)} (95%: ${percent(p.capabilityCI[0])}–${percent(p.capabilityCI[1])})</dd></dl>
      <p class="small">Our hypothesis H1: at least one category reaches 80% precision.</p></div>
    <section><h2>Agreement between raters: Cohen's kappa</h2><p>If two people label the same items and often agree, the labels are trustworthy. But some agreement happens by chance. <b>Kappa</b> counts only agreement beyond chance: 1 is perfect, 0 is what guessing would give.</p>
      <div class="formula">kappa = (observed agreement − chance agreement) ÷ (1 − chance agreement)</div></section>
    <div class="worked"><p class="eyebrow">Try it: two raters, yes or no</p>
      <div class="tbl"><table><thead><tr><th></th><th>Rater B: yes</th><th>Rater B: no</th></tr></thead><tbody>
        ${["yes", "no"].map((lab, i) => html`<tr><th>Rater A: ${lab}</th>${[0, 1].map((j) => html`<td><input type="number" min="0" aria-label=${`A ${lab}, B ${j ? "no" : "yes"}`} value=${t[i][j]} onInput=${(e) => setCell(i, j, e.target.value)} style="max-width:90px" /></td>`)}</tr>`)}</tbody></table></div>
      <dl class="kv"><dt>Items</dt><dd>${k.n}</dd><dt>Observed agreement</dt><dd>(${t[0][0]} + ${t[1][1]}) ÷ ${k.n} = ${f2(k.observed, 3)}</dd>
        <dt>Chance agreement</dt><dd>${f2(k.expected, 3)}</dd><dt>Kappa</dt><dd>${f2(k.kappa, 3)}: ${kappaWords(k.kappa)}</dd></dl>
      <p class="small">Chance agreement = (A says yes × B says yes + A says no × B says no) ÷ items². Try 40, 5, 5, 0: the raters agree on 80% of items, yet kappa is below zero, because both say yes almost every time and would agree that often by chance.</p></div>
    <section><h2>Our plan and dates</h2><ul>
      <li><b>Drift (18 pairs):</b> Jerad and Leticia label independently by Oct 16; kappa between them. Neither opens the other's labels until both are in (the blindness rule).</li>
      <li><b>Signals (147 items) and lineage (58 pairs):</b> Jerad labels by Oct 13 and again at least 14 days later on a 30% subset; the agreement with himself (intra-rater kappa) is reported and labelled as such.</li>
      <li><b>Scoring:</b> <code>python scripts/annotation_kit.py score</code> by Oct 27.</li></ul>
      <p class="small">Labelling happens in the <b>labelling studio</b>, a page on your own computer. Its briefing explains the task, the safety rules, and how to decide. Beside each item it shows the rule, the guideline's examples, and a step-through of the decision order, and it never fills in a label for you. Open it with <code>windows/3-open-labelling-page.bat</code>, and after each session save with <code>4-save-my-labels.bat</code>. See <a href=${LINKS.file("docs/validation/README.md")} target="_blank" rel="noopener">the validation guide</a>.</p></section>
    <${Where} items=${[["Precision and kappa", "src/msr_pipeline/validation.py"], ["The labelling guideline", "docs/validation/ANNOTATION_GUIDELINE.md"]]} />`;
}

function Sensitivity() {
  return html`<${Unvalidated} /><section><h2>Why</h2><p>Every analysis makes choices: where the high-risk cutoff is, which skills count, how to treat extremely popular ones. If a different reasonable choice flipped the result, we should not trust it. So the headline numbers are recomputed under six scenarios.</p></section>
    <section><h2>The six scenarios</h2><${Table} name="sensitivity_summary.csv">${(rows) => html`<div class="tbl"><table><thead><tr><th>Scenario</th><th class="r">Flagged share</th><th class="r">Copies ratio</th><th class="r">p</th><th class="r">Effect r</th></tr></thead><tbody>
      ${rows.map((x) => html`<tr><td>${x.scenario}</td><td class="r">${percent(num(x.high_risk_share))}</td><td class="r">${f2(num(x.mean_copies_ratio))}</td><td class="r">${f2(num(x.mwu_p_copies), 4)}</td><td class="r">${f2(num(x.rank_biserial_copies), 3)}</td></tr>`)}</tbody></table></div>
      <p class="small">In all six, flagged skills average more copies (ratio above 1), the difference stays significant, and the effect stays small. The share flagged moves with the cutoff, as expected: stricter cutoffs flag fewer skills.</p>`}<//></section>
    <${Where} items=${[["The scenarios", "src/msr_pipeline/analysis.py (sensitivity_summary)"], ["The table", "results/sensitivity_summary.csv"]]} />`;
}

function Environments() {
  return html`<section><h2>Why test in more than one place</h2><p>The assignment requires that “the main pipeline runs from a clean environment or documented container” and that “a new user can follow the README to reproduce the primary results”. Running the pipeline on different computers and getting the same numbers proves that.</p><${EnvDiagram} /></section>
    <section><h2>What “the same” means</h2><p>Each result table is compared with the committed one. It matches if it is identical, or if the only differences are numbers within one part in a billion: Linux and Windows round the last digits of the regression differently. Anything else is reported as a difference.</p></section>
    <section><h2>1. Windows, by double-clicking (no git, no commands)</h2><ol>
      <li>Install Python 3.11 or newer from <a href="https://www.python.org/downloads/" target="_blank" rel="noopener">python.org</a>; tick <b>Add python.exe to PATH</b>.</li>
      <li>Download the project: on the <a href=${LINKS.repo} target="_blank" rel="noopener">repository page</a>, green <b>Code</b> button, <b>Download ZIP</b>. Extract it to <code>C:\\dev\\</code>, not OneDrive.</li>
      <li>In the <code>windows</code> folder, double-click <code>1-set-up.bat</code> (about 3 minutes), then <code>2-run-pipeline.bat</code> (about 3 minutes).</li>
      <li>A report opens in Notepad. Send it with <a href="#/docs/freshrun">Record a fresh-run check</a>.</li></ol>
      <p class="small muted">How it was made: <code>windows/*.bat</code> call <code>scripts/fresh_run_check.py</code>, which reruns the analysis into <code>build/fresh_run/</code> and never touches <code>results/</code>.</p></section>
    <section><h2>2. Docker (any computer with Docker Desktop)</h2><p>A container is a clean, sealed computer inside yours, built from a recipe (the <code>Dockerfile</code>). Ours pins the exact Python and package versions that produced the committed results.</p>
      <ol><li>Install <a href="https://www.docker.com/products/docker-desktop/" target="_blank" rel="noopener">Docker Desktop</a> and start it.</li>
        <li>Open a terminal (Windows: PowerShell) and run:</li></ol>
      <div class="formula" style="white-space:pre">docker build -t group9-p01 https://github.com/jeraddunne/csc580-group9-msr2027.git#main\ndocker run --rm -v group9-data:/app/data/samples group9-p01</div>
      <p>It prints four stages and a summary: sample downloaded, tests, analysis matches, spec checks. Recorded on Sep 30: all four pass, 14 of 14 tables match. If the build says it cannot find a Dockerfile, the container has not reached <code>main</code> yet (pull request #72).</p>
      <p class="small muted">How it was made: <code>Dockerfile</code>, <code>docker/constraints.txt</code> (the pinned versions), <code>docker/check.sh</code> (the four stages).</p></section>
    <section><h2>3. Linux or WSL, following the README</h2><div class="formula" style="white-space:pre">sudo apt install -y python3-venv make git\ngit clone https://github.com/jeraddunne/csc580-group9-msr2027.git && cd csc580-group9-msr2027\nmake setup && make data && make test && make pipeline</div>
      <p class="small">Tested on a fresh Ubuntu 26.04. The first try found a real bug: the README's <code>make setup</code> needed <code>python</code>, which Ubuntu does not have. The fix is in pull request #72.</p></section>
    <section><h2>4. GitHub's computers</h2><p>On GitHub: <b>Actions</b> → <b>Container check</b> → <b>Run workflow</b>. It builds the container on a fresh machine none of us owns and shows the summary on the run page.</p></section>
    <section><h2>Make your own environment</h2><p>Any recipe works if it installs the package, downloads the sample, and runs <code>scripts/fresh_run_check.py</code>. Record where you ran it and what matched in <a href=${LINKS.file("docs/REPRODUCE.md")} target="_blank" rel="noopener">docs/REPRODUCE.md</a>. A run on your own computer by someone other than the author is what the sprint reviews ask for.</p></section>`;
}

function Git() {
  const rows = [
    ["Repository", "The project folder on GitHub: every document, the code, the results.", "Everything the guide shows comes from it."],
    ["main", "The approved version of the project.", "Never changed directly; only by merging reviewed pull requests."],
    ["Issue", "A task or a question, with comments.", "Tasks, New task, comments, Mark done."],
    ["Board", "The issues arranged by status: Todo, In progress, Block, Done.", "The Board tab and the status box on each task."],
    ["Milestone", "A sprint: a group of issues with a due date.", "The Sprint dropdowns and the Sprints page."],
    ["Branch", "A private copy for one change.", "Made for you when you press Send in Documents."],
    ["Commit", "A saved change, with the author's name and a message.", "Made for you, under your name."],
    ["Pull request", "“Please add this change to main”, with a place to discuss it.", "Opened for you; follow it in Reviews."],
    ["Review", "A teammate reads the pull request and approves it or asks for changes.", "Reviews: Approve or Ask for changes."],
    ["Merge", "Adding an approved pull request to main.", "Done by the Product Owner."],
  ];
  return html`<${GitDiagram} />
    <section><h2>The words, and where they are in this guide</h2><div class="tbl"><table><thead><tr><th>Word</th><th>Meaning</th><th>In the guide</th></tr></thead><tbody>
      ${rows.map(([a, b, c]) => html`<tr><td><b>${a}</b></td><td>${b}</td><td>${c}</td></tr>`)}</tbody></table></div></section>
    <section><h2>Why it works this way</h2><p>Two people see every change before it counts. That catches mistakes, spreads knowledge, and gives the course visible evidence that everyone contributed: the rubric checks issues, pull requests, and reviews by each member.</p></section>`;
}

function Safety() {
  return html`<section><h2>The rules</h2><ul>
      <li><b>Never run anything from the dataset.</b> Skills can contain real commands. We only read text. If you ever suspect something is actively malicious, stop and tell Jerad; the instructor is informed before anything else happens.</li>
      <li><b>No names from the dataset.</b> Reports show counts, never repository or account names.</li>
      <li><b>No personal information in the project.</b> It is public: no emails, phone numbers, or addresses.</li>
      <li><b>Label on your own.</b> While labelling, never open another rater's files (for example anything ending <code>_jd_r1.csv</code>), and do not discuss items until both labels are in.</li>
      <li><b>Your work under your name.</b> Nobody signs, labels, or reviews for someone else.</li>
      <li><b>Disclose AI help.</b> If an AI tool materially helped, add an entry: <a href="#/docs/ailog">Add an AI-use entry</a>.</li>
      <li><b>Keep your GitHub key private.</b> Never paste it into chat or email.</li></ul></section>
    <${Where} items=${[["Threats and safe reporting", "THREATS_TO_VALIDITY.md"], ["Team charter", "TEAM_CHARTER.md"], ["AI-use log", "ai-use-log.md"]]} />`;
}

function Glossary() {
  const terms = [
    ["Skill", "A folder with SKILL.md that tells an AI coding assistant how to do a job."],
    ["GitSkills", "The dataset of skills from public GitHub projects (MSR 2027 Mining Challenge)."],
    ["Distinct skill", "One unique text; its copies are counted separately."],
    ["Rule", "A text pattern with a risk category and a severity from 1 to 10."],
    ["High risk", "A skill where a rule with severity 6 or more matches."],
    ["Signal", "A rule match: a hint, not proof."],
    ["Prevalence", "How common something is: a share."],
    ["Confidence interval", "The range of values that fits the data; we use 95%."],
    ["Shingle", "A run of five consecutive words."],
    ["Jaccard similarity", "Shared chunks divided by all chunks; 1 is identical."],
    ["Lineage pair", "Two versions of a skill with similarity 0.5 or more."],
    ["Drift", "A risky category added or removed between versions."],
    ["Mann-Whitney U", "A comparison of two groups by ranks rather than averages."],
    ["Rank-biserial r", "Effect size of that comparison, from −1 to 1."],
    ["Negative binomial (NB2)", "A regression model for counts with many zeros and a few big values."],
    ["IRR", "Incidence rate ratio: how many times more, all else equal."],
    ["p-value", "How surprising the data would be if there were no real difference."],
    ["Holm adjustment", "A correction for running many tests at once."],
    ["Precision", "The share of flags a person confirms."],
    ["Cohen's kappa", "Agreement between raters beyond chance."],
    ["Blindness rule", "Raters do not see each other's labels until both are in."],
    ["Sensitivity check", "Redoing the analysis with other reasonable choices."],
    ["Reproducible", "Someone else gets the same results from the same code and data."],
    ["Container", "A clean, sealed computer inside yours, built from a recipe."],
    ["DMAIC", "Define, Measure, Analyze, Improve, Control: the Lean Six Sigma phases our sprints follow."],
    ["Kaizen", "A small, measured process improvement."],
    ["ADR", "Architecture (or any) decision record: why we decided something."],
  ];
  return html`<div class="tbl"><table><tbody>${terms.map(([a, b]) => html`<tr><td style="width:30%"><b>${a}</b></td><td>${b}</td></tr>`)}</tbody></table></div>`;
}

const BODIES = {
  project: Project,
  pipeline: Pipeline,
  rules: Rules,
  prevalence: Prevalence,
  similarity: Similarity,
  reach: Reach,
  regression: Regression,
  holm: Holm,
  validation: Validation,
  sensitivity: Sensitivity,
  environments: Environments,
  git: Git,
  safety: Safety,
  glossary: Glossary,
};
