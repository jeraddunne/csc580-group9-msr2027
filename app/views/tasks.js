import { html, useApp, useData, useState, Loaded, StatusChip, Avatars, Labels, Select, GitHubHTML, RequireSignIn, Inline, when, STATUS_CLASS } from "../lib/ui.js";
import { loadProject, statusOf } from "../lib/data.js";
import { checklistProgress, parseChecklist, setChecklistItem, TASK_TYPES } from "../lib/tasks.js";
import { explain } from "../lib/github.js";
import { TEAM, memberByLogin } from "../content/project.js";

const STATUSES = ["Todo", "In progress", "Block", "Done", "Cancelled"];

export function Tasks({ query }) {
  const app = useApp();
  const project = useData("project", loadProject);
  const [view, setView] = useState(query.view || (app.me ? "mine" : "all"));
  const [sprint, setSprint] = useState(query.sprint || "");
  const [type, setType] = useState("");
  const [status, setStatus] = useState("");
  const [person, setPerson] = useState("");
  const [showClosed, setShowClosed] = useState(false);

  return html`
    <section class="page-head row between">
      <div class="stack"><p class="eyebrow">Backlog, board, and your work</p><h1>Tasks</h1></div>
      <a class="btn primary" href="#/new">New task</a>
    </section>
    <div class="tabs" role="tablist">
      ${[["mine", "My tasks"], ["all", "All tasks"], ["board", "Board"]].map(([v, label]) => html`<button role="tab" aria-selected=${view === v} class=${view === v ? "on" : ""} onClick=${() => setView(v)}>${label}</button>`)}
    </div>
    ${view === "mine" && !app.me ? html`<${RequireSignIn} what="see your tasks" />` : html`<${Loaded} state=${project} what="Loading tasks">${(p) => {
      const sprints = p.milestones.map((m) => m.title);
      let list = p.issues;
      if (view === "mine") list = list.filter((i) => i.assignees.some((a) => a.login === app.me.login));
      if (sprint) list = list.filter((i) => i.milestone?.title === sprint);
      if (type) list = list.filter((i) => i.labels.some((l) => l.name === `type:${type}`));
      if (person) list = list.filter((i) => (person === "none" ? !i.assignees.length : i.assignees.some((a) => a.login === person)));
      if (status) list = list.filter((i) => statusOf(i, p.board) === status);
      if (!showClosed && view !== "board") list = list.filter((i) => i.state === "open");
      return html`
        <div class="filters">
          <div class="field"><label for="f-sprint">Sprint</label><${Select} id="f-sprint" value=${sprint} onChange=${setSprint} options=${sprints} placeholder="All sprints" /></div>
          <div class="field"><label for="f-type">Type</label><${Select} id="f-type" value=${type} onChange=${setType} options=${TASK_TYPES} placeholder="All types" /></div>
          ${view !== "mine" && html`<div class="field"><label for="f-person">Person</label><${Select} id="f-person" value=${person} onChange=${setPerson} options=${[{ value: "none", label: "Nobody yet" }, ...TEAM.map((m) => ({ value: m.login, label: m.name }))]} placeholder="Everyone" /></div>`}
          ${view !== "board" && html`<div class="field"><label for="f-status">Status</label><${Select} id="f-status" value=${status} onChange=${setStatus} options=${STATUSES} placeholder="Any status" /></div>`}
          ${view !== "board" && html`<label class="check small"><input type="checkbox" checked=${showClosed} onChange=${(e) => setShowClosed(e.target.checked)} />Show finished tasks</label>`}
        </div>
        ${p.boardError && html`<p class="small muted">Board status is unavailable (${explain(p.boardError)}); open tasks show as Todo.</p>`}
        ${view === "board" ? html`<${Board} list=${list} board=${p.board} />` : html`<${TaskList} list=${list} board=${p.board} empty=${view === "mine" ? "Nothing matches. Pick a task from All tasks, or create one." : "No tasks match these filters."} />`}`;
    }}<//>`}`;
}

function TaskList({ list, board, empty }) {
  if (!list.length) return html`<p class="muted">${empty}</p>`;
  return html`<div class="card" style="padding-top:4px;padding-bottom:4px"><div class="tasks">
    ${list.map((i) => {
      const prog = checklistProgress(i.body);
      return html`<a class="task-row" href=${`#/task/${i.number}`}>
        <span class="t">#${i.number} ${i.title}</span><${StatusChip} status=${statusOf(i, board)} />
        <span class="meta"><${Avatars} users=${i.assignees} /><span>${i.milestone?.title || "no sprint"}</span>
          ${prog.total ? html`<span>${prog.done}/${prog.total} steps</span>` : ""}<${Labels} labels=${i.labels} /></span></a>`;
    })}
  </div></div>`;
}

function Board({ list, board }) {
  const app = useApp();
  const [moving, setMoving] = useState(null);
  const canMove = app.me && (board.size > 0 || app.practice);
  async function move(issue, to) {
    const item = board.get(issue.number);
    setMoving(issue.number);
    try {
      let itemId = item?.itemId;
      if (!itemId) itemId = await app.gh.addToBoard(issue.node_id);
      await app.gh.setBoardField(itemId, "Status", to);
      app.say(`#${issue.number} moved to ${to}.`);
      app.refresh();
    } catch (e) {
      app.say(explain(e));
    } finally {
      setMoving(null);
    }
  }
  const columns = ["Todo", "In progress", "Block", "Done"];
  return html`${!canMove && html`<p class="small muted">${app.me ? "Moving cards needs the project box on your key." : "Sign in to move cards."}</p>`}
    <div class="board">${columns.map((col) => {
      const cards = list.filter((i) => statusOf(i, board) === col);
      return html`<div class="col"><h3><span><span class=${`chip ${STATUS_CLASS[col]}`}>${col}</span></span><span class="muted num">${cards.length}</span></h3>
        ${cards.slice(0, col === "Done" ? 15 : 60).map((i) => html`<div class="bcard">
          <a href=${`#/task/${i.number}`}>#${i.number} ${i.title}</a>
          <div class="row between"><${Avatars} users=${i.assignees} /><span class="tiny muted">${i.milestone?.title || ""}</span></div>
          ${canMove && html`<select aria-label=${`Move #${i.number}`} value=${col} disabled=${moving === i.number} onChange=${(e) => move(i, e.target.value)}>
            ${STATUSES.map((s) => html`<option value=${s}>${s === col ? `In ${s}` : `Move to ${s}`}</option>`)}</select>`}
        </div>`)}
        ${col === "Done" && cards.length > 15 ? html`<p class="tiny muted">and ${cards.length - 15} more</p>` : ""}
      </div>`;
    })}</div>`;
}

export function TaskDetail({ number }) {
  const issue = useData(`issue-${number}`, (gh) => gh.issue(number), [number]);
  const comments = useData(`comments-${number}`, (gh) => gh.commentsHtml(number), [number]);
  const project = useData("project", loadProject);
  return html`<p class="crumbs"><a href="#/tasks">Tasks</a> / #${number}</p>
    <${Loaded} state=${issue} what="Loading the task">${(i) => i.pull_request
      ? html`<div class="note info">#${number} is a pull request. <a href=${`#/review/${number}`}>Open it in Reviews</a>.</div>`
      : html`<${TaskView} key=${i.updated_at} issue=${i} comments=${comments} project=${project} />`}<//>`;
}

function TaskView({ issue, comments, project }) {
  const app = useApp();
  const [body, setBody] = useState(issue.body || "");
  const [busy, setBusy] = useState(null);
  const [comment, setComment] = useState("");
  const [finishing, setFinishing] = useState(false);
  const items = parseChecklist(body);
  const mine = app.me && issue.assignees.some((a) => a.login === app.me.login);
  const status = project.data ? statusOf(issue, project.data.board) : issue.state === "closed" ? "Done" : "Todo";
  const canWrite = app.me?.canWrite;

  async function tick(item, done) {
    setBusy(`step-${item.index}`);
    try {
      const fresh = await app.gh.issue(issue.number);
      const next = setChecklistItem(fresh.body || "", item.index, done, item.text);
      if (next === null) {
        setBody(fresh.body || "");
        app.say("The steps changed on GitHub meanwhile; the page now shows the latest. Tick again.");
        return;
      }
      await app.gh.updateIssue(issue.number, { body: next });
      setBody(next);
      if (done && status === "Todo" && app.me) setStatusTo("In progress", true);
    } catch (e) {
      app.say(explain(e));
    } finally {
      setBusy(null);
    }
  }

  async function setStatusTo(to, quiet) {
    setBusy("status");
    try {
      let itemId = project.data?.board.get(issue.number)?.itemId;
      if (!itemId) itemId = await app.gh.addToBoard(issue.node_id);
      await app.gh.setBoardField(itemId, "Status", to);
      if (!quiet) app.say(`Status set to ${to}.`);
      app.refresh();
    } catch (e) {
      if (!quiet) app.say(explain(e));
    } finally {
      setBusy(null);
    }
  }

  async function post(e) {
    e.preventDefault();
    if (!comment.trim()) return;
    setBusy("comment");
    try {
      await app.gh.comment(issue.number, comment.trim());
      setComment("");
      app.say("Comment posted.");
      app.refresh();
    } catch (err) {
      app.say(explain(err));
    } finally {
      setBusy(null);
    }
  }

  async function assign(add) {
    setBusy("assign");
    try {
      const logins = issue.assignees.map((a) => a.login).filter((l) => l !== app.me.login);
      await app.gh.updateIssue(issue.number, { assignees: add ? [...logins, app.me.login] : logins });
      app.say(add ? "The task is yours." : "You are no longer on this task.");
      app.refresh();
    } catch (e) {
      app.say(explain(e));
    } finally {
      setBusy(null);
    }
  }

  async function finish(e) {
    e.preventDefault();
    if (!comment.trim()) return;
    setBusy("finish");
    try {
      await app.gh.comment(issue.number, `Done: ${comment.trim()}`);
      await app.gh.updateIssue(issue.number, { state: "closed", state_reason: "completed" });
      try {
        let itemId = project.data?.board.get(issue.number)?.itemId;
        if (!itemId) itemId = await app.gh.addToBoard(issue.node_id);
        await app.gh.setBoardField(itemId, "Status", "Done");
      } catch {
        // Closing the task is what counts; the board catches up with its own rule.
      }
      setComment("");
      setFinishing(false);
      app.say("Task marked done.");
      app.refresh();
    } catch (err) {
      app.say(explain(err));
    } finally {
      setBusy(null);
    }
  }

  async function reopen() {
    setBusy("reopen");
    try {
      await app.gh.updateIssue(issue.number, { state: "open" });
      app.say("Task reopened.");
      app.refresh();
    } catch (e) {
      app.say(explain(e));
    } finally {
      setBusy(null);
    }
  }

  const done = items.filter((x) => x.done).length;
  return html`
    <section class="page-head">
      <p class="eyebrow">Task #${issue.number} · ${issue.milestone?.title || "no sprint"}</p>
      <h1>${issue.title}</h1>
      <div class="row small"><${StatusChip} status=${status} /><span class="muted">for</span><${Avatars} users=${issue.assignees} /><${Labels} labels=${issue.labels} />
        <a href=${issue.html_url} target="_blank" rel="noopener">Open on GitHub</a></div>
    </section>
    <div class="grid two" style="align-items:start">
      <div class="stack" style="gap:16px">
        ${items.length > 0 && html`<div class="card">
          <div class="row between"><h2>Steps</h2><span class="small num">${done} of ${items.length} done</span></div>
          <ul class="checklist">${items.map((it) => html`<li class=${it.done ? "done" : ""}>
            <input type="checkbox" id=${`step-${it.index}`} checked=${it.done} disabled=${!canWrite || busy !== null} onChange=${(e) => tick(it, e.target.checked)} />
            <label for=${`step-${it.index}`}><span><${Inline} text=${it.text} /></span></label>${busy === `step-${it.index}` ? html`<span class="spinner"></span>` : ""}</li>`)}</ul>
          ${!app.me && html`<p class="small muted"><a href="#/signin">Sign in</a> to tick steps.</p>`}
        </div>`}
        <div class="card"><h2>Details</h2><${GitHubHTML} html=${issue.body_html} /></div>
      </div>
      <div class="stack" style="gap:16px">
        <div class="card">
          <h2>What you can do</h2>
          ${!app.me ? html`<${RequireSignIn} what="work on this task" />` : !canWrite ? html`<div class="note warn">Accept the repository invitation to work on tasks.</div>` : html`
            <div class="row">
              ${issue.state === "open" && !mine && html`<button class="btn primary" disabled=${busy} onClick=${() => assign(true)}>Take this task</button>`}
              ${issue.state === "open" && mine && html`<button class="btn" disabled=${busy} onClick=${() => assign(false)}>Give it back</button>`}
              ${issue.state === "open" && html`<button class="btn" disabled=${busy} onClick=${() => setFinishing(!finishing)}>Mark done</button>`}
              ${issue.state === "closed" && html`<button class="btn" disabled=${busy} onClick=${reopen}>Reopen</button>`}
            </div>
            ${(project.data?.board.size > 0 || app.practice) && html`<div class="field"><label for="st">Board status</label>
              <select id="st" value=${status} disabled=${busy} onChange=${(e) => setStatusTo(e.target.value)}>${STATUSES.map((s) => html`<option value=${s}>${s}</option>`)}</select>
              <span class="hint">Todo, In progress, Block if you are stuck, Done.</span></div>`}
            ${finishing && html`<form class="form note" onSubmit=${finish}>
              <label for="done-text"><b>What did you do?</b> One or two sentences, with a link to your pull request if there is one. This becomes a comment, then the task closes.</label>
              <textarea id="done-text" value=${comment} onInput=${(e) => setComment(e.target.value)}></textarea>
              <div class="row"><button class="btn primary" disabled=${!comment.trim() || busy}>Close as done</button><button type="button" class="btn link" onClick=${() => setFinishing(false)}>Cancel</button></div>
            </form>`}`}
        </div>
        <div class="card">
          <h2>Comments</h2>
          <${Loaded} state=${comments} what="Loading comments">${(cs) => cs.length
            ? cs.map((c) => html`<div class="comment"><div class="row small"><b>${memberByLogin(c.user.login)?.name || c.user.login}</b><span class="muted">${when(c.created_at)}</span></div><${GitHubHTML} html=${c.body_html} /></div>`)
            : html`<p class="small muted">No comments yet. Stuck? Say which step you are on and what you see.</p>`}<//>
          ${app.me && canWrite && !finishing && html`<form class="form" onSubmit=${post}>
            <label for="c" class="small"><b>Add a comment</b> in plain words. Type @ and a GitHub name to notify someone, for example @angel06la.</label>
            <textarea id="c" value=${comment} onInput=${(e) => setComment(e.target.value)}></textarea>
            <div><button class="btn primary" disabled=${!comment.trim() || busy}>${busy === "comment" ? "Posting…" : "Post comment"}</button></div>
          </form>`}
        </div>
      </div>
    </div>`;
}

