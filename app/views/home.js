import { html, useApp, useData, Loaded, Bar, StatusChip, when } from "../lib/ui.js";
import { loadProject, milestoneByTitle, statusOf, rawFile } from "../lib/data.js";
import { checklistProgress, daysBetween, isoDate } from "../lib/tasks.js";
import { charterRow } from "../lib/docs.js";
import { KEY_DATES, QUESTION, currentPhase, memberByLogin } from "../content/project.js";

export function Home() {
  const app = useApp();
  const today = isoDate();
  const phase = currentPhase(today);
  const project = useData("project", loadProject);
  const pulls = useData("pulls-open", (gh) => gh.pulls("open"));
  const charter = useData("charter", () => rawFile("TEAM_CHARTER.md"));

  const day = Math.min(daysBetween(phase.start, today) + 1, daysBetween(phase.start, phase.end) + 1);
  const length = daysBetween(phase.start, phase.end) + 1;
  const next = KEY_DATES.filter((k) => k.date >= today).slice(0, 3);

  return html`
    <section class="page-head">
      <p class="eyebrow">${new Date().toLocaleDateString(undefined, { weekday: "long", month: "long", day: "numeric" })}</p>
      <h1>${app.me ? `Hi ${app.member?.name.split(" ")[0] || app.me.login}` : "Welcome to the Group 9 Project Guide"}</h1>
      <p class="lede">${app.me
        ? "Here is where the project stands and what is yours to do next."
        : "Everything about our project in one place: what we study, how it works, what each sprint needs, and your tasks. Sign in to work on tasks and documents; you can look around first."}</p>
    </section>

    ${!app.me && html`<div class="card accent"><div class="row between"><div class="stack"><h2>New here? Start with these</h2>
      <p class="small">1. <a href="#/learn/project">The project in five minutes</a> · 2. <a href="#/practice">Practise safely</a> · 3. <a href="#/signin">Sign in</a> (3 minutes) · 4. <a href="#/docs/charter">Sign the charter</a></p></div>
      <a class="btn primary" href="#/signin">Sign in</a></div></div>`}

    <div class="grid">
      <div class="card">
        <p class="eyebrow">Now: ${phase.name}${phase.dmaic ? ` · ${phase.dmaic}` : ""}</p>
        <h2>${phase.deliverable || phase.purpose}</h2>
        <p class="small muted">Day ${Math.max(day, 1)} of ${length} · ends ${when(phase.end + "T12:00:00")}${phase.weight ? ` · ${phase.weight}% of the grade` : ""}</p>
        <${Bar} value=${Math.max(day, 0)} total=${length} />
        <${Loaded} state=${project} what="Loading sprint progress">${(p) => {
          const m = phase.milestone && milestoneByTitle(p.milestones, phase.milestone);
          if (!m) return html`<p class="small">${phase.purpose}</p>`;
          const tasks = p.issues.filter((i) => i.milestone?.number === m.number);
          const closed = tasks.filter((i) => i.state === "closed").length;
          return html`<div class="stack"><div class="row between small"><span>Tasks finished in ${phase.name}</span><b class="num">${closed} of ${tasks.length}</b></div>
            <${Bar} value=${closed} total=${tasks.length} good /></div>`;
        }}<//>
        <a class="btn" href="#/sprints">See what ${phase.name} needs</a>
      </div>

      <div class="card">
        <p class="eyebrow">Coming up</p>
        <ul class="stack" style="list-style:none;margin:0;padding:0">
          ${next.map((k) => html`<li class="row"><span class="label">${when(k.date + "T12:00:00")}</span><span class="small">${k.text}</span></li>`)}
        </ul>
        <p class="small muted">The research question:</p>
        <p class="small">${QUESTION}</p>
        <a class="btn" href="#/learn/project">What that means, in plain words</a>
      </div>
    </div>

    ${app.me && html`<${MyWork} project=${project} pulls=${pulls} charter=${charter} />`}

    <div class="card">
      <div class="row between"><h2>Recently changed</h2><button class="btn link" onClick=${app.refresh}>Refresh</button></div>
      <${Loaded} state=${project} what="Loading recent changes">${(p) => html`<div class="tasks">
        ${p.issues.slice(0, 6).map((i) => html`<a class="task-row" href=${`#/task/${i.number}`}>
          <span class="t">#${i.number} ${i.title}</span><${StatusChip} status=${statusOf(i, p.board)} />
          <span class="meta"><span>updated ${when(i.updated_at)}</span><span>${i.milestone?.title || "no sprint"}</span></span></a>`)}
      </div>`}<//>
    </div>`;
}

function MyWork({ project, pulls, charter }) {
  const app = useApp();
  const login = app.me.login;
  const member = app.member;
  return html`<div class="grid two">
    <div class="card">
      <div class="row between"><h2>Your tasks</h2><a class="btn link" href="#/tasks?view=mine">All of yours</a></div>
      <${Loaded} state=${project} what="Loading your tasks">${(p) => {
        const mine = p.issues.filter((i) => i.state === "open" && i.assignees.some((a) => a.login === login));
        if (!mine.length)
          return html`<p class="small">Nothing is assigned to you. <a href="#/tasks">Browse the tasks</a> and pick one, or <a href="#/new">create one</a>.</p>`;
        return html`<div class="tasks">${mine.slice(0, 6).map((i) => {
          const prog = checklistProgress(i.body);
          return html`<a class="task-row" href=${`#/task/${i.number}`}><span class="t">#${i.number} ${i.title}</span><${StatusChip} status=${statusOf(i, p.board)} />
            <span class="meta"><span>${i.milestone?.title || "no sprint"}</span>${prog.total ? html`<span>${prog.done} of ${prog.total} steps</span>` : ""}</span></a>`;
        })}</div>`;
      }}<//>
    </div>
    <div class="card">
      <h2>Your checklist as a member</h2>
      <${Loaded} state=${charter} what="Checking the charter">${(text) => {
        const signed = Boolean(member && charterRow(text, member.name)?.signed);
        return html`<ul class="rubric">
          <li><span class=${`tick ${app.me.canWrite ? "on" : ""}`}>${app.me.canWrite ? "✓" : ""}</span><span>Accepted the invitation and signed in</span><span></span></li>
          <li><span class=${`tick ${signed ? "on" : ""}`}>${signed ? "✓" : ""}</span><span>Signed the team charter</span>${signed ? html`<span class="small muted">done</span>` : html`<a class="small" href="#/docs/charter">Sign it</a>`}</li>
          <li><span class="tick"></span><span>Filled in your profile</span><a class="small" href="#/docs/profile">Open</a></li>
        </ul>`;
      }}<//>
      <h3>Waiting for your review</h3>
      <${Loaded} state=${pulls} what="Loading pull requests">${(list) => {
        const asked = list.filter((pr) => pr.requested_reviewers?.some((r) => r.login === login));
        const others = list.filter((pr) => pr.user.login !== login && !asked.includes(pr));
        if (!asked.length && !others.length) return html`<p class="small muted">No open pull requests.</p>`;
        return html`<div class="tasks">${[...asked, ...others].slice(0, 4).map((pr) => html`<a class="task-row" href=${`#/review/${pr.number}`}>
          <span class="t">#${pr.number} ${pr.title}</span>${asked.includes(pr) ? html`<span class="chip waiting">asked you</span>` : html`<span class="chip plain">open</span>`}
          <span class="meta">by ${memberByLogin(pr.user.login)?.name || pr.user.login} · ${when(pr.updated_at)}</span></a>`)}</div>`;
      }}<//>
    </div>
  </div>`;
}

