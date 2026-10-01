import { html, useApp, useData, useState, Loaded, Select, RequireSignIn } from "../lib/ui.js";
import { loadProject } from "../lib/data.js";
import { PRIORITIES, TASK_TYPES, guidedTaskBody, isoDate, taskProblems } from "../lib/tasks.js";
import { explain } from "../lib/github.js";
import { TEAM, currentPhase } from "../content/project.js";

const TYPE_HELP = {
  research: "framing, analysis design, interpretation",
  pipeline: "code that loads, scans, or analyses data",
  data: "getting or describing the dataset",
  docs: "README, process documents, decisions",
  test: "automated tests or validation",
  process: "Scrum and Lean Six Sigma work, meetings, reviews",
  report: "writing the report or its figures",
  presentation: "the demo and slides",
};

export function NewTask({ query }) {
  const app = useApp();
  const project = useData("project", loadProject);
  const phase = currentPhase(isoDate());
  const [t, setT] = useState({
    title: query.title || "",
    type: query.type || "",
    sprint: query.sprint || phase.milestone || "",
    priority: "Medium",
    assignee: app.me?.login || "",
    due: "",
    time: "",
    why: "",
    need: "",
    steps: ["", "", ""],
    doneWhen: "",
  });
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState(null);
  const [made, setMade] = useState(null);
  const [tried, setTried] = useState(false);
  const set = (k) => (v) => setT((s) => ({ ...s, [k]: v }));
  const setStep = (i, v) => setT((s) => ({ ...s, steps: s.steps.map((x, j) => (j === i ? v : x)) }));
  const move = (i, d) =>
    setT((s) => {
      const steps = [...s.steps];
      const j = i + d;
      if (j < 0 || j >= steps.length) return s;
      [steps[i], steps[j]] = [steps[j], steps[i]];
      return { ...s, steps };
    });
  const problems = taskProblems(t);

  async function create(milestones) {
    setTried(true);
    if (problems.length) return;
    setBusy(true);
    setError(null);
    try {
      const m = milestones.find((x) => x.title === t.sprint);
      const issue = await app.gh.createIssue({
        title: t.title.trim(),
        body: guidedTaskBody(t),
        labels: ["guided-task", `type:${t.type}`, `priority:${t.priority.toLowerCase()}`],
        milestone: m?.number,
        assignees: t.assignee ? [t.assignee] : [],
      });
      const notes = [];
      try {
        const itemId = await app.gh.addToBoard(issue.node_id);
        await app.gh.setBoardField(itemId, "Status", "Todo");
        await app.gh.setBoardField(itemId, "Priority", t.priority);
        await app.gh.setBoardField(itemId, "Work type", t.type);
        if (m) await app.gh.setBoardField(itemId, "Sprint", t.sprint);
        if (t.due) await app.gh.setBoardDate(itemId, "Target date", t.due);
      } catch (e) {
        notes.push(`It is not on the board yet (${explain(e)}).`);
      }
      setMade({ issue, notes });
      app.refresh();
    } catch (e) {
      setError(explain(e));
    } finally {
      setBusy(false);
    }
  }

  if (made)
    return html`<section class="page-head"><p class="eyebrow">Created</p><h1>#${made.issue.number} ${made.issue.title}</h1></section>
      ${app.practice
        ? html`<div class="note ok"><b>Practice: this task would now be on GitHub and the board, under your name.</b><span>Nothing was sent.</span></div>`
        : html`<div class="note ok"><b>The task is on GitHub, under your name.</b>${made.notes.map((n) => html`<span>${n}</span>`)}</div>`}
      <div class="row">${!app.practice && html`<a class="btn primary" href=${`#/task/${made.issue.number}`}>Open the task</a>`}
        <button class="btn" onClick=${() => { setMade(null); setTried(false); setT((s) => ({ ...s, title: "", why: "", need: "", steps: ["", "", ""], doneWhen: "", time: "", due: "" })); }}>Create another</button>
        ${app.practice ? html`<a class="btn link" href="#/practice">See the practice log</a>` : html`<a class="btn link" href=${made.issue.html_url} target="_blank" rel="noopener">See it on GitHub</a>`}</div>`;

  return html`<section class="page-head"><p class="eyebrow">Plan work for yourself or the team</p><h1>New task</h1>
      <p class="lede">A good task says why it matters, lists small steps someone new could follow, and says how to tell it is done. The task goes on GitHub and the board under your name.</p></section>
    <${RequireSignIn} what="create tasks">
      <${Loaded} state=${project} what="Loading sprints">${(p) => html`<div class="grid two" style="align-items:start">
        <form class="card form" onSubmit=${(e) => { e.preventDefault(); create(p.milestones); }}>
          <div class="field"><label for="n-title">Title</label>
            <input id="n-title" type="text" value=${t.title} onInput=${(e) => set("title")(e.target.value)} placeholder="Say the result, not the activity: “Charter signed by Hina”" /></div>
          <div class="fields">
            <div class="field"><label for="n-type">Type</label><${Select} id="n-type" value=${t.type} onChange=${set("type")} placeholder="Choose…" options=${TASK_TYPES.map((x) => ({ value: x, label: `${x}: ${TYPE_HELP[x]}` }))} /></div>
            <div class="field"><label for="n-sprint">Sprint</label><${Select} id="n-sprint" value=${t.sprint} onChange=${set("sprint")} placeholder="Choose…" options=${p.milestones.filter((m) => m.state === "open").map((m) => m.title)} /></div>
            <div class="field"><label for="n-pri">Priority</label><${Select} id="n-pri" value=${t.priority} onChange=${set("priority")} options=${PRIORITIES} /></div>
            <div class="field"><label for="n-who">Who does it</label><${Select} id="n-who" value=${t.assignee} onChange=${set("assignee")} placeholder="Nobody yet" options=${TEAM.map((m) => ({ value: m.login, label: m.name }))} /></div>
            <div class="field"><label for="n-due">Due</label><input id="n-due" type="date" value=${t.due} onInput=${(e) => set("due")(e.target.value)} /></div>
            <div class="field"><label for="n-time">Time needed</label><input id="n-time" type="text" value=${t.time} onInput=${(e) => set("time")(e.target.value)} placeholder="About 20 minutes" /></div>
          </div>
          <div class="field"><label for="n-why">Why this matters</label><textarea id="n-why" value=${t.why} onInput=${(e) => set("why")(e.target.value)} placeholder="Name the sprint deliverable or deadline it serves."></textarea></div>
          <div class="field"><label for="n-need">What you need before you start <span class="muted">(optional)</span></label><textarea id="n-need" value=${t.need} onInput=${(e) => set("need")(e.target.value)} placeholder="- Signed in to the guide"></textarea></div>
          <div class="field"><span class="flabel">Steps</span><span class="hint">One action per step, starting with a verb. They become checkboxes.</span>
            <div class="steps-edit">${t.steps.map((s, i) => html`<div class="step"><span class="n">${i + 1}.</span>
              <input type="text" aria-label=${`Step ${i + 1}`} value=${s} onInput=${(e) => setStep(i, e.target.value)} placeholder=${i === 0 ? "Open …" : ""} />
              <span class="row" style="gap:2px"><button type="button" class="btn link" aria-label="Move up" onClick=${() => move(i, -1)}>↑</button><button type="button" class="btn link" aria-label="Move down" onClick=${() => move(i, 1)}>↓</button>
              <button type="button" class="btn link" aria-label="Remove step" onClick=${() => setT((x) => ({ ...x, steps: x.steps.filter((_, j) => j !== i) }))}>✕</button></span></div>`)}</div>
            <div><button type="button" class="btn" onClick=${() => setT((x) => ({ ...x, steps: [...x.steps, ""] }))}>Add a step</button></div></div>
          <div class="field"><label for="n-done">Done when</label><textarea id="n-done" value=${t.doneWhen} onInput=${(e) => set("doneWhen")(e.target.value)} placeholder="Something anyone can check: a merged pull request, a file, a number."></textarea></div>
          ${tried && problems.length > 0 && html`<div class="note warn" role="alert"><b>Almost there</b>${problems.map((x) => html`<span>${x}</span>`)}</div>`}
          ${error && html`<div class="note bad" role="alert">${error}</div>`}
          <div class="row"><button class="btn primary" disabled=${busy}>${busy ? "Creating…" : "Create task"}</button></div>
        </form>
        <div class="card"><p class="eyebrow">Preview: what GitHub will show</p><h3>${t.title || "Title"}</h3>
          <div class="row small"><span class="label">guided-task</span>${t.type && html`<span class="label">type:${t.type}</span>`}<span class="label">priority:${t.priority.toLowerCase()}</span><span class="label">${t.sprint || "no sprint"}</span></div>
          <pre class="md" style="white-space:pre-wrap;font-family:var(--f-mono);font-size:0.78rem;background:var(--surface-2);padding:10px;border-radius:6px;max-height:520px;overflow:auto">${guidedTaskBody(t)}</pre></div>
      </div>`}<//>
    <//>`;
}
