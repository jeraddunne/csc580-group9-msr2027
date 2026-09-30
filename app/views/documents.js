import { html, useApp, useData, useState, Loaded, Select, RequireSignIn } from "../lib/ui.js";
import { explain } from "../lib/github.js";
import { rawFile } from "../lib/data.js";
import { branchName, isoDate } from "../lib/tasks.js";
import {
  PROFILE_FIELDS,
  appendAiUseRow,
  charterRow,
  freshRunPath,
  freshRunRecord,
  meetingNote,
  meetingNotePath,
  signCharter,
  updateProfile,
} from "../lib/docs.js";
import { LINKS, TEAM } from "../content/project.js";

const FORMS = [
  { id: "charter", title: "Sign the team charter", who: "Every member, once", what: "Adds today's date to your row in section 14 of TEAM_CHARTER.md.", time: "10 minutes, most of it reading" },
  { id: "profile", title: "Fill in your profile", who: "Every member", what: "Updates your page in docs/team/: time zone, hours, strengths, role preferences.", time: "5 minutes" },
  { id: "meeting", title: "Add meeting notes", who: "The note taker of a meeting", what: "Creates docs/meeting-notes/<date>-<type>.md from the meeting template.", time: "10 minutes after a meeting" },
  { id: "freshrun", title: "Record a fresh-run check", who: "Whoever ran windows/2-run-pipeline.bat or the container", what: "Saves the check's report in docs/lean-six-sigma/metrics/, the evidence for S1-10 and the gemba walk.", time: "2 minutes" },
  { id: "ailog", title: "Add an AI-use entry", who: "Anyone who used an AI tool for project work", what: "Adds one row to ai-use-log.md, which the rubric requires.", time: "3 minutes" },
];

function prBody({ purpose, closes, what }) {
  return [
    "## Purpose",
    "",
    closes ? `Closes #${closes}` : "No linked issue.",
    "",
    purpose,
    "",
    "## What changed",
    "",
    `- ${what}`,
    "",
    "## How it was tested",
    "",
    "Document change made with the Group 9 Project Guide, which changes only this file. Previewed in the guide before sending.",
    "",
    "## Generated outputs",
    "",
    "None.",
    "",
    "## Reviewer checklist (reviewer fills; must be a member other than the author)",
    "",
    "- [ ] Read the change in Files changed",
    "- [ ] Acceptance criterion of the linked issue is met",
    "- [ ] Approval comment states what was verified",
    "",
    "_Sent with the Group 9 Project Guide._",
  ].join("\n");
}

export function Documents({ form }) {
  if (!form)
    return html`<section class="page-head"><p class="eyebrow">Change project files without git</p><h1>Documents</h1>
        <p class="lede">Each form below changes one file. When you send it, the guide makes a pull request under your name and asks a teammate to review it. Nothing changes in the project until a teammate approves it, so you cannot break anything.</p></section>
      <div class="lessons">${FORMS.map((f) => html`<a class="lesson-card" href=${`#/docs/${f.id}`}><span class="k">${f.time}</span><h3>${f.title}</h3><p class="small">${f.what}</p><p class="tiny muted">For: ${f.who}</p></a>`)}</div>
      <div class="note small"><b>What happens when you press Send</b><span>1. A copy of the project is made for your change (a branch). 2. Your change is saved in that copy (a commit, with your name). 3. A pull request asks the team to add it. 4. A teammate reviews and approves it, and the Product Owner merges it. You can follow it in Reviews.</span></div>`;
  const meta = FORMS.find((f) => f.id === form);
  if (!meta) return html`<div class="note warn">No such form. <a href="#/docs">All forms</a>.</div>`;
  const Form = { charter: CharterForm, profile: ProfileForm, meeting: MeetingForm, freshrun: FreshRunForm, ailog: AiLogForm }[form];
  return html`<p class="crumbs"><a href="#/docs">Documents</a> / ${meta.title}</p>
    <section class="page-head"><h1>${meta.title}</h1><p class="lede">${meta.what}</p></section>
    <${RequireSignIn} what="change project documents"><${Form} /><//>`;
}

// Shared: reviewer choice, send button, and the result.
function useSend() {
  const app = useApp();
  const [state, setState] = useState({ busy: false, error: null, pr: null });
  async function send(args) {
    setState({ busy: true, error: null, pr: null });
    try {
      const pr = await app.gh.proposeFileChange(args);
      setState({ busy: false, error: null, pr });
      app.refresh();
    } catch (e) {
      setState({ busy: false, error: explain(e), pr: null });
    }
  }
  return [state, send];
}

function Reviewer({ value, onChange }) {
  const app = useApp();
  const others = TEAM.filter((m) => m.login !== app.me?.login);
  return html`<div class="field"><label for="rev">Who should review it</label>
    <${Select} id="rev" value=${value} onChange=${onChange} options=${others.map((m) => ({ value: m.login, label: `${m.name} (${m.role})` }))} />
    <span class="hint">Anyone but you. Leticia (Scrum Master) is a good default.</span></div>`;
}

function Sent({ state, children }) {
  if (state.pr?.practice)
    return html`<div class="note ok" role="status"><b>Practice: this would have opened pull request #${state.pr.number} under your name.</b>
      <span>Nothing was sent. It would change <code>${state.pr.path}</code> as shown below and ask your reviewer to check it.</span>
      <details><summary class="small">The file as it would be</summary><pre class="md" style="white-space:pre-wrap;font-family:var(--f-mono);font-size:0.75rem;max-height:360px;overflow:auto">${state.pr.text}</pre></details>
      <span class="row"><a class="btn" href="#/practice">See the practice log</a></span></div>`;
  if (state.pr)
    return html`<div class="note ok" role="status"><b>Sent. Pull request #${state.pr.number} is waiting for review.</b>
      <span>It is under your name on GitHub. When it is approved and merged, the change appears in the project.</span>
      <span class="row"><a class="btn primary" href=${`#/review/${state.pr.number}`}>Follow it</a><a class="btn link" href=${state.pr.html_url} target="_blank" rel="noopener">See it on GitHub</a></span></div>`;
  return html`${state.error && html`<div class="note bad" role="alert">${state.error}</div>`}${children}`;
}

function CharterForm() {
  const app = useApp();
  const me = app.member;
  const [read, setRead] = useState(false);
  const [date, setDate] = useState(isoDate());
  const [reviewer, setReviewer] = useState("angel06la");
  const [state, send] = useSend();
  const charter = useData("charter", () => rawFile("TEAM_CHARTER.md"));
  if (!me) return html`<div class="note warn">Your GitHub name (${app.me.login}) is not one of the four members, so there is no charter row to sign.</div>`;
  const ref = me.onboarding ? `#${me.onboarding}` : "";
  return html`<${Loaded} state=${charter} what="Reading the charter">${(text) => {
    let preview = null;
    let problem = null;
    try {
      const after = signCharter(text, me.name, date, ref || "this pull request");
      preview = charterRow(after, me.name)?.line;
    } catch (e) {
      problem = e.message;
    }
    return html`<div class="card form">
      <p>The charter is our working agreement: how we plan, review, decide, and handle problems. Read it before you sign: <a href=${LINKS.file("TEAM_CHARTER.md")} target="_blank" rel="noopener">TEAM_CHARTER.md on GitHub</a>, or the <a href=${LINKS.site + "TEAM_CHARTER/"} target="_blank" rel="noopener">easier-to-read version</a>.</p>
      <label class="check"><input type="checkbox" checked=${read} onChange=${(e) => setRead(e.target.checked)} /><span>I have read the charter and agree to it.</span></label>
      <div class="fields"><div class="field"><label for="d">Date</label><input id="d" type="date" value=${date} onInput=${(e) => setDate(e.target.value)} /></div>
        <${Reviewer} value=${reviewer} onChange=${setReviewer} /></div>
      ${problem ? html`<div class="note warn">${problem}</div>` : html`<div class="stack"><span class="small muted">Your row will read:</span><div class="formula">${preview}</div></div>`}
      <${Sent} state=${state}><div class="row"><button class="btn primary" disabled=${!read || problem || state.busy} onClick=${() => send({
        path: "TEAM_CHARTER.md",
        branch: branchName("process", me.onboarding, `sign-charter-${me.name.split(" ")[0]}`),
        change: (old) => signCharter(old, me.name, date, ref || "this pull request"),
        message: `Sign the team charter (${me.name})`,
        title: `Sign the team charter (${me.name})`,
        body: prBody({ purpose: `${me.name} signs TEAM_CHARTER.md section 14.`, closes: me.onboarding, what: "TEAM_CHARTER.md: my row in section 14 now has the date and my onboarding issue." }),
        reviewers: [reviewer],
      })}>${state.busy ? "Sending…" : "Sign and send for review"}</button></div><//>
    </div>`;
  }}<//>`;
}

function ProfileForm() {
  const app = useApp();
  const me = app.member;
  const [a, setA] = useState({});
  const [reviewer, setReviewer] = useState("angel06la");
  const [state, send] = useSend();
  const current = useData(`profile-${me?.login}`, () => (me ? rawFile(me.profile) : null));
  if (!me) return html`<div class="note warn">Your GitHub name is not one of the four members, so there is no profile page to fill.</div>`;
  const set = (k) => (e) => setA((s) => ({ ...s, [k]: e.target.value }));
  const valueOf = (text, label) => text.split(/\r?\n/).find((l) => l.split("|")[1]?.trim() === label)?.split("|")[2]?.trim() || "";
  return html`<${Loaded} state=${current} what="Reading your profile">${(text) => html`<div class="card form">
    <p class="small">Leave a box empty to keep what is there now. No email or phone number: the project is public.</p>
    <div class="fields">${PROFILE_FIELDS.map((f) => html`<div class="field"><label for=${f}>${f}</label><input id=${f} type="text" placeholder=${valueOf(text, f) || ""} value=${a[f] || ""} onInput=${set(f)} /></div>`)}</div>
    <div class="fields">${["Sprint 1", "Sprint 2", "Sprint 3"].map((s) => html`<div class="field"><label for=${s}>Role you would like in ${s}</label>
      <${Select} id=${s} value=${a[`Role preference ${s}`] || ""} onChange=${(v) => setA((x) => ({ ...x, [`Role preference ${s}`]: v }))} placeholder=${valueOf(text, s) || "No preference"} options=${["Product Owner", "Scrum Master", "Developer / Researcher", "Any"]} /></div>`)}</div>
    <div class="field"><label for="st">Strengths I bring</label><textarea id="st" value=${a.strengths || ""} onInput=${set("strengths")} placeholder="One per line"></textarea></div>
    <div class="field"><label for="le">What I want to learn</label><textarea id="le" value=${a.learn || ""} onInput=${set("learn")} placeholder="One per line"></textarea></div>
    <div class="field"><label for="ws">Working style notes</label><textarea id="ws" value=${a.workingStyle || ""} onInput=${set("workingStyle")} placeholder="How you like feedback, when you work best"></textarea></div>
    <${Reviewer} value=${reviewer} onChange=${setReviewer} />
    <${Sent} state=${state}><div><button class="btn primary" disabled=${state.busy || !Object.values(a).some((v) => String(v).trim())} onClick=${() => send({
      path: me.profile,
      branch: branchName("docs", me.onboarding, `profile-${me.name.split(" ")[0]}`),
      change: (old) => updateProfile(old, a),
      message: `Update my profile (${me.name})`,
      title: `Update my profile (${me.name})`,
      body: prBody({ purpose: `${me.name} fills in their team profile.`, closes: null, what: `${me.profile}: filled-in fields.` }),
      reviewers: [reviewer],
    })}>${state.busy ? "Sending…" : "Send for review"}</button></div><//>
  </div>`}<//>`;
}

function MeetingForm() {
  const app = useApp();
  const [m, setM] = useState({ type: "checkin", date: isoDate(), time: "", location: "", facilitator: "Leticia Aderhold", noteTaker: app.member?.name || "", attendees: [], agenda: "", notes: "", decisions: [{ decision: "", rationale: "", adr: false }], actions: [{ action: "", owner: "", due: "", issue: "" }], parking: "" });
  const [reviewer, setReviewer] = useState("angel06la");
  const [state, send] = useSend();
  const set = (k) => (e) => setM((s) => ({ ...s, [k]: e.target.value }));
  const names = TEAM.map((t) => t.name);
  let path = "";
  let problem = null;
  try {
    path = meetingNotePath(m.date, m.type);
  } catch (e) {
    problem = e.message;
  }
  const upd = (list, i, k, v) => setM((s) => ({ ...s, [list]: s[list].map((x, j) => (j === i ? { ...x, [k]: v } : x)) }));
  return html`<div class="card form">
    <div class="fields">
      <div class="field"><label for="mt">Meeting type</label><${Select} id="mt" value=${m.type} onChange=${(v) => setM((s) => ({ ...s, type: v }))} options=${["kickoff", "planning", "checkin", "review", "retro", "standup"]} /></div>
      <div class="field"><label for="md">Date</label><input id="md" type="date" value=${m.date} onInput=${set("date")} /></div>
      <div class="field"><label for="mtm">Time</label><input id="mtm" type="text" value=${m.time} onInput=${set("time")} placeholder="18:00" /></div>
      <div class="field"><label for="mf">Facilitator</label><${Select} id="mf" value=${m.facilitator} onChange=${(v) => setM((s) => ({ ...s, facilitator: v }))} options=${names} /></div>
      <div class="field"><label for="mn">Note taker</label><${Select} id="mn" value=${m.noteTaker} onChange=${(v) => setM((s) => ({ ...s, noteTaker: v }))} options=${names} placeholder="Choose…" /></div>
      <div class="field"><label for="ml">Where</label><input id="ml" type="text" value=${m.location} onInput=${set("location")} placeholder="Video call (no links)" /></div>
    </div>
    <fieldset class="field" style="border:0;padding:0;margin:0"><legend class="flabel">Who came</legend><div class="row">${[...names, "Instructor (if present)"].map((n) => html`<label class="check"><input type="checkbox" checked=${m.attendees.includes(n)} onChange=${(e) => setM((s) => ({ ...s, attendees: e.target.checked ? [...s.attendees, n] : s.attendees.filter((x) => x !== n) }))} />${n}</label>`)}</div></fieldset>
    <div class="field"><label for="ma">Agenda</label><textarea id="ma" value=${m.agenda} onInput=${set("agenda")} placeholder="One item per line"></textarea></div>
    <div class="field"><label for="mno">Notes</label><textarea id="mno" value=${m.notes} onInput=${set("notes")} placeholder="One point per line"></textarea></div>
    <div class="field"><span class="flabel">Decisions</span>${m.decisions.map((d, i) => html`<div class="fields"><input type="text" aria-label="Decision" placeholder="Decision" value=${d.decision} onInput=${(e) => upd("decisions", i, "decision", e.target.value)} /><input type="text" aria-label="Why" placeholder="Why" value=${d.rationale} onInput=${(e) => upd("decisions", i, "rationale", e.target.value)} /><label class="check small"><input type="checkbox" checked=${d.adr} onChange=${(e) => upd("decisions", i, "adr", e.target.checked)} />Needs a decision record (ADR)</label></div>`)}
      <div><button type="button" class="btn" onClick=${() => setM((s) => ({ ...s, decisions: [...s.decisions, { decision: "", rationale: "", adr: false }] }))}>Add a decision</button></div></div>
    <div class="field"><span class="flabel">Action items</span>${m.actions.map((a, i) => html`<div class="fields"><input type="text" aria-label="Action" placeholder="Action" value=${a.action} onInput=${(e) => upd("actions", i, "action", e.target.value)} />
      <${Select} value=${a.owner} onChange=${(v) => upd("actions", i, "owner", v)} options=${names} placeholder="Owner" /><input type="date" aria-label="Due" value=${a.due} onInput=${(e) => upd("actions", i, "due", e.target.value)} /><input type="text" aria-label="Issue number" placeholder="Issue #, if any" value=${a.issue} onInput=${(e) => upd("actions", i, "issue", e.target.value)} /></div>`)}
      <div><button type="button" class="btn" onClick=${() => setM((s) => ({ ...s, actions: [...s.actions, { action: "", owner: "", due: "", issue: "" }] }))}>Add an action</button></div></div>
    <div class="field"><label for="mp">Parking lot</label><textarea id="mp" value=${m.parking} onInput=${set("parking")} placeholder="Topics for another time"></textarea></div>
    <${Reviewer} value=${reviewer} onChange=${setReviewer} />
    ${problem && html`<div class="note warn">${problem}</div>`}
    <details><summary class="small">Preview the file (${path || "…"})</summary><pre class="md" style="white-space:pre-wrap;font-family:var(--f-mono);font-size:0.78rem">${meetingNote(m)}</pre></details>
    <${Sent} state=${state}><div><button class="btn primary" disabled=${problem || state.busy || !m.noteTaker} onClick=${() => send({
      path,
      branch: branchName("docs", null, `meeting-notes-${m.date}-${m.type}`),
      change: (old) => {
        if (old !== null) throw new Error(`Notes for a ${m.type} meeting on ${m.date} already exist. Change the date or the type.`);
        return meetingNote(m);
      },
      message: `Add ${m.type} meeting notes for ${m.date}`,
      title: `Meeting notes: ${m.type}, ${m.date}`,
      body: prBody({ purpose: `Notes from the ${m.type} meeting on ${m.date}.`, closes: null, what: `${path}: new file from the meeting template.` }),
      reviewers: [reviewer],
    })}>${state.busy ? "Sending…" : "Send for review"}</button></div><//>
  </div>`;
}

function FreshRunForm() {
  const app = useApp();
  const me = app.member;
  const [report, setReport] = useState("");
  const [reviewer, setReviewer] = useState("angel06la");
  const [state, send] = useSend();
  const date = isoDate();
  let problem = null;
  let text = "";
  try {
    text = report.trim() ? freshRunRecord(report, me?.name || app.me.login) : "";
  } catch (e) {
    problem = e.message;
  }
  const path = freshRunPath(date, app.me.login);
  return html`<div class="card form">
    <ol class="small" style="margin:0;padding-left:1.2em">
      <li>Run the check on your own computer: <a href="#/learn/environments">how, step by step</a>. With the Windows files it is <code>2-run-pipeline.bat</code>; with Docker it is the two commands on that page.</li>
      <li>Open the report it saved, <code>build\\fresh_run\\REPORT.md</code> (the Windows file opens it in Notepad for you), select everything (Ctrl+A) and copy (Ctrl+C).</li>
      <li>Paste it below and send it.</li>
    </ol>
    <div class="field"><label for="rp">The report</label><textarea id="rp" style="min-height:200px;font-family:var(--f-mono);font-size:0.8rem" value=${report} onInput=${(e) => setReport(e.target.value)} placeholder="# Fresh-run check …"></textarea></div>
    ${problem && html`<div class="note warn">${problem}</div>`}
    ${text && /\| no:/.test(text) && html`<div class="note warn small">The report says the results did not match. Send it anyway: a difference is a finding, not your mistake. Add a comment on #19 too.</div>`}
    <${Reviewer} value=${reviewer} onChange=${setReviewer} />
    <p class="small muted">Saved as <code>${path}</code>.</p>
    <${Sent} state=${state}><div><button class="btn primary" disabled=${!text || problem || state.busy} onClick=${() => send({
      path,
      branch: branchName("process", 19, `fresh-run-${app.me.login}`),
      change: () => text,
      message: `Record a fresh-run check (${me?.name || app.me.login})`,
      title: `Fresh-run check on ${me?.name || app.me.login}'s computer`,
      body: prBody({ purpose: "Evidence for the measurement system check (S1-10) and the sprint review's gemba walk. Refs #19.", closes: null, what: `${path}: the report from scripts/fresh_run_check.py.` }),
      reviewers: [reviewer],
    })}>${state.busy ? "Sending…" : "Send for review"}</button></div><//>
  </div>`;
}

function AiLogForm() {
  const app = useApp();
  const name = app.member?.name || app.me.login;
  const [r, setR] = useState({ date: isoDate(), member: name, tool: "", what: "", where: "", verifiedBy: name, how: "" });
  const [reviewer, setReviewer] = useState("angel06la");
  const [state, send] = useSend();
  const set = (k) => (e) => setR((s) => ({ ...s, [k]: e.target.value }));
  const ready = Object.values(r).every((v) => String(v).trim());
  return html`<div class="card form">
    <p class="small">The rubric requires every material use of an AI tool to be disclosed and checked by a person. Small autocomplete does not need an entry; anything you would not have written the same way without the tool does.</p>
    <div class="fields">
      <div class="field"><label for="a1">Date</label><input id="a1" type="date" value=${r.date} onInput=${set("date")} /></div>
      <div class="field"><label for="a2">Tool and model</label><input id="a2" type="text" value=${r.tool} onInput=${set("tool")} placeholder="ChatGPT (GPT-5), Claude, Copilot…" /></div>
      <div class="field"><label for="a3">Verified by</label><${Select} id="a3" value=${r.verifiedBy} onChange=${(v) => setR((s) => ({ ...s, verifiedBy: v }))} options=${TEAM.map((t) => t.name)} /></div>
    </div>
    <div class="field"><label for="a4">What it was used for</label><textarea id="a4" value=${r.what} onInput=${set("what")} placeholder="Drafted the meeting notes from my bullet points"></textarea></div>
    <div class="field"><label for="a5">Where the output is</label><input id="a5" type="text" value=${r.where} onInput=${set("where")} placeholder="File, pull request, or issue: docs/meeting-notes/2026-10-01-checkin.md" /></div>
    <div class="field"><label for="a6">How it was checked</label><textarea id="a6" value=${r.how} onInput=${set("how")} placeholder="Read every line against my own notes and fixed two dates"></textarea></div>
    <${Reviewer} value=${reviewer} onChange=${setReviewer} />
    <${Sent} state=${state}><div><button class="btn primary" disabled=${!ready || state.busy} onClick=${() => send({
      path: "ai-use-log.md",
      branch: branchName("docs", 40, `ai-use-${app.me.login}-${r.date}`),
      change: (old) => appendAiUseRow(old, r),
      message: `Add an AI-use entry (${name}, ${r.date})`,
      title: `AI-use log entry: ${name}, ${r.date}`,
      body: prBody({ purpose: "Discloses AI assistance, as the rubric requires. Refs #40.", closes: null, what: "ai-use-log.md: one new row." }),
      reviewers: [reviewer],
    })}>${state.busy ? "Sending…" : "Send for review"}</button></div><//>
  </div>`;
}
