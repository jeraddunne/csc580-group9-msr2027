import { html, useApp, useData, useState, Loaded, GitHubHTML, RequireSignIn, when } from "../lib/ui.js";
import { explain } from "../lib/github.js";
import { memberByLogin } from "../content/project.js";

const nameOf = (login) => memberByLogin(login)?.name || login;

export function Reviews() {
  const app = useApp();
  const pulls = useData("pulls-open", (gh) => gh.pulls("open"));
  return html`<section class="page-head"><p class="eyebrow">Every change is checked by someone else</p><h1>Reviews</h1>
      <p class="lede">Before a change joins the project, a member other than its author reads it and approves it. Reviewing counts as your contribution, and the sprint reviews check that everyone does it. You do not need to understand code to review a document: check that it says what it should and that its links and numbers are right.</p></section>
    <${Loaded} state=${pulls} what="Loading open pull requests">${(list) => {
      if (!list.length) return html`<p class="muted">No pull requests are waiting.</p>`;
      const me = app.me?.login;
      const asked = list.filter((p) => p.requested_reviewers?.some((r) => r.login === me));
      const mine = list.filter((p) => p.user.login === me);
      const rest = list.filter((p) => !asked.includes(p) && !mine.includes(p));
      const section = (title, items, empty) => html`<div class="card"><h2>${title}</h2>${items.length ? html`<div class="tasks">${items.map((p) => html`<a class="task-row" href=${`#/review/${p.number}`}>
        <span class="t">#${p.number} ${p.title}</span><span class="chip plain">${p.draft ? "draft" : "open"}</span>
        <span class="meta">by ${nameOf(p.user.login)} · updated ${when(p.updated_at)}${p.requested_reviewers?.length ? ` · review asked from ${p.requested_reviewers.map((r) => nameOf(r.login)).join(", ")}` : ""}</span></a>`)}</div>` : html`<p class="small muted">${empty}</p>`}</div>`;
      return html`${me && section("Asked of you", asked, "Nobody has asked you for a review right now.")}
        ${section("Others you can review", rest, "None.")}
        ${me && section("Yours, waiting for others", mine, "You have no open pull requests.")}`;
    }}<//>`;
}

function Diff({ patch }) {
  if (!patch) return html`<p class="small muted">No text changes to show (a binary file or a very large change). Open it on GitHub.</p>`;
  return html`<div class="diff">${patch.split("\n").map((l) => html`<div class=${l.startsWith("@@") ? "h" : l.startsWith("+") ? "a" : l.startsWith("-") ? "d" : ""}>${l || " "}</div>`)}</div>`;
}

export function ReviewDetail({ number }) {
  const app = useApp();
  const pr = useData(`pr-${number}`, (gh) => gh.pull(number), [number]);
  const files = useData(`pr-files-${number}`, (gh) => gh.pullFiles(number), [number]);
  const reviews = useData(`pr-reviews-${number}`, (gh) => gh.reviews(number), [number]);
  const [text, setText] = useState("");
  const [busy, setBusy] = useState(false);
  const [done, setDone] = useState(null);

  async function submit(event) {
    setBusy(true);
    try {
      await app.gh.review(number, event, text.trim());
      setDone(event);
      setText("");
      app.refresh();
    } catch (e) {
      app.say(explain(e));
    } finally {
      setBusy(false);
    }
  }

  return html`<p class="crumbs"><a href="#/reviews">Reviews</a> / #${number}</p>
    <${Loaded} state=${pr} what="Loading the pull request">${(p) => {
      const own = app.me && p.user.login === app.me.login;
      return html`<section class="page-head"><p class="eyebrow">Pull request #${p.number} · by ${nameOf(p.user.login)} · ${p.state === "open" ? (p.merged ? "merged" : "open") : p.merged_at ? "merged" : "closed"}</p>
          <h1>${p.title}</h1><div class="row small"><span class="label">${p.head.ref}</span><span class="muted">into</span><span class="label">${p.base.ref}</span>
          <span>${p.changed_files} file${p.changed_files === 1 ? "" : "s"}, +${p.additions} −${p.deletions}</span><a href=${p.html_url} target="_blank" rel="noopener">Open on GitHub</a></div></section>
        <div class="grid two" style="align-items:start">
          <div class="stack" style="gap:16px">
            <div class="card"><h2>What the author says</h2><${GitHubHTML} html=${p.body_html} /></div>
            <div class="card"><h2>What changed</h2><p class="small muted">Green lines are added, red lines are removed, grey lines show where in the file.</p>
              <${Loaded} state=${files} what="Loading the changes">${(fs) => fs.map((f) => html`<details open=${fs.length <= 3}><summary class="small"><code>${f.filename}</code> <span class="muted">${f.status}, +${f.additions} −${f.deletions}</span></summary><${Diff} patch=${f.patch} /></details>`)}<//>
            </div>
          </div>
          <div class="stack" style="gap:16px">
            <div class="card"><h2>Reviews so far</h2>
              <${Loaded} state=${reviews} what="Loading reviews">${(rs) => rs.length
                ? rs.map((r) => html`<div class="comment"><div class="row small"><b>${nameOf(r.user.login)}</b><span class=${`chip ${r.state === "APPROVED" ? "done" : r.state === "CHANGES_REQUESTED" ? "block" : "plain"}`}>${r.state.replace("_", " ").toLowerCase()}</span><span class="muted">${when(r.submitted_at)}</span></div>${r.body && html`<p class="small">${r.body}</p>`}</div>`)
                : html`<p class="small muted">No reviews yet.</p>`}<//>
            </div>
            <div class="card">
              <h2>Your review</h2>
              ${!app.me ? html`<${RequireSignIn} what="review" />` : own ? html`<p class="small">This is your own pull request. Someone else reviews it; you can reply to them on GitHub.</p>` : p.state !== "open" ? html`<p class="small">This pull request is closed.</p>` : done ? html`<div class="note ok"><b>Review sent: ${done.replace("_", " ").toLowerCase()}.</b><span>It is on GitHub under your name.</span></div>` : html`
                <ol class="small" style="margin:0;padding-left:1.2em">
                  <li>Read what the author says it does.</li>
                  <li>Read the changes: does the file now say that? Are names, dates, links, and numbers right?</li>
                  <li>If a number is quoted, check it against the file it names.</li>
                  <li>Write what you checked. “Looks good” is not enough; “Checked the three dates against the schedule” is.</li>
                </ol>
                <div class="field"><label for="rv">What did you check?</label><textarea id="rv" value=${text} onInput=${(e) => setText(e.target.value)}></textarea></div>
                <div class="row">
                  <button class="btn primary" disabled=${busy || text.trim().length < 15} onClick=${() => submit("APPROVE")}>Approve</button>
                  <button class="btn" disabled=${busy || text.trim().length < 15} onClick=${() => submit("REQUEST_CHANGES")}>Ask for changes</button>
                  <button class="btn link" disabled=${busy || !text.trim()} onClick=${() => submit("COMMENT")}>Comment only</button>
                </div>
                <p class="tiny muted">At least 15 characters, so the review says what was verified.</p>`}
            </div>
          </div>
        </div>`;
    }}<//>`;
}
