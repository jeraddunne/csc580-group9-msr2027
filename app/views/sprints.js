import { html, useData, Loaded, Bar, when } from "../lib/ui.js";
import { loadProject, milestoneByTitle } from "../lib/data.js";
import { daysBetween, isoDate } from "../lib/tasks.js";
import { END, LINKS, PHASES, START, currentPhase } from "../content/project.js";

export function Sprints() {
  const today = isoDate();
  const now = currentPhase(today);
  const project = useData("project", loadProject);
  const span = daysBetween(START, END) + 1;
  const todayAt = Math.min(Math.max(daysBetween(START, today) + 0.5, 0), span);

  return html`
    <section class="page-head">
      <p class="eyebrow">Scrum sprints with a Lean Six Sigma (DMAIC) overlay</p>
      <h1>Phases and sprints</h1>
      <p class="lede">The course has six phases. Each ends with a review where we show the deliverables below, quoted from the assignment. A deliverable is done when its task on GitHub is closed, so this page is always current.</p>
    </section>

    <figure class="card">
      <div class="diagram-wrap"><svg class="diagram" viewBox="0 0 900 96" role="img" aria-label=${`Semester timeline from ${START} to ${END}; today is in ${now.name}.`} style="min-width:640px">
        ${PHASES.map((p) => {
          const x = 10 + (880 * daysBetween(START, p.start)) / span;
          const w = (880 * (daysBetween(p.start, p.end) + 1)) / span - 3;
          const cls = p.id === now.id ? "box-a" : p.end < today ? "box" : "box-d";
          return html`<g><rect class=${cls} x=${x} y="30" width=${w} height="30" rx="4" />
            <text class="tb" x=${x + 6} y="20" style="font-size:12px">${p.short || p.name}</text>
            <text class="tl" x=${x + 6} y="76">${p.weight ? `${p.weight}%` : ""}</text></g>`;
        })}
        <line x1=${10 + (880 * todayAt) / span} x2=${10 + (880 * todayAt) / span} y1="24" y2="66" stroke="currentColor" stroke-width="2" />
        <text class="tm" x=${10 + (880 * todayAt) / span} y="92" text-anchor="middle">today</text>
      </svg></div>
      <figcaption>Solid blue is now. Percentages are shares of the grade; individual reflections are another 5%.</figcaption>
    </figure>

    <${Loaded} state=${project} what="Loading deliverables">${(p) => html`<div class="phases">
      ${PHASES.filter((ph) => ph.id !== "break").map((ph) => html`<${PhaseCard} phase=${ph} project=${p} now=${ph.id === now.id} past=${ph.end < today} />`)}
    </div>`}<//>`;
}

function PhaseCard({ phase, project, now, past }) {
  const m = phase.milestone && milestoneByTitle(project.milestones, phase.milestone);
  const byNumber = new Map(project.issues.map((i) => [i.number, i]));
  const items = phase.rubric.map((r) => {
    const issues = r.issues.map((n) => byNumber.get(n)).filter(Boolean);
    const done = issues.length > 0 && issues.every((i) => i.state === "closed");
    return { ...r, issues: issues, done };
  });
  const doneCount = items.filter((i) => i.done).length;
  const tasks = project.issues.filter((i) => i.milestone?.title === phase.milestone);
  const tasksDone = tasks.filter((i) => i.state === "closed").length;
  return html`<details class=${`card phase${now ? " now" : ""}`} open=${now}>
    <summary style="cursor:pointer;list-style:none">
      <div class="row between">
        <div class="stack" style="gap:2px">
          <p class="eyebrow">${phase.dmaic ? `${phase.dmaic} · ` : ""}${when(phase.start + "T12:00:00")} to ${when(phase.end + "T12:00:00")}${now ? " · now" : past ? " · finished" : ""}</p>
          <h2>${phase.name}${phase.deliverable ? `: ${phase.deliverable}` : ""}</h2>
        </div>
        <span class="small num">${doneCount} of ${items.length} deliverables${m ? ` · ${tasksDone}/${tasks.length} tasks` : ""}</span>
      </div>
      <div style="margin-top:8px"><${Bar} value=${doneCount} total=${items.length} good /></div>
    </summary>
    <p class="small">${phase.purpose}</p>
    <ul class="rubric">
      ${items.map((it) => html`<li><span class=${`tick ${it.done ? "on" : ""}`}>${it.done ? "✓" : ""}</span><span>${it.text}</span>
        <span class="small">${it.issues.length
          ? it.issues.map((i) => html`<a href=${`#/task/${i.number}`}>#${i.number}</a> `)
          : html`<span class="muted">evidence at the review</span>`}</span></li>`)}
    </ul>
    ${phase.acceptance && html`<div class="note small"><b>Accepted when</b><span>${phase.acceptance}</span></div>`}
    ${phase.youCan?.length > 0 && html`<div class="stack"><h3>What you can do in this phase</h3>
      <ul style="margin:0;padding-left:1.2em" class="small">${phase.youCan.map((y) => html`<li>${y}</li>`)}</ul></div>`}
    <div class="row">
      ${m && html`<a class="btn" href=${`#/tasks?view=all&sprint=${encodeURIComponent(phase.milestone)}`}>All ${phase.name} tasks</a>`}
      ${phase.review && html`<a class="btn link" href=${LINKS.file(phase.review)} target="_blank" rel="noopener">Review document on GitHub</a>`}
    </div>
  </details>`;
}
