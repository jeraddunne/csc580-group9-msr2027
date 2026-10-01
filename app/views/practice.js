import { html, useApp, useState, Select } from "../lib/ui.js";
import { TEAM } from "../content/project.js";

export function PracticeStart({ compact }) {
  const app = useApp();
  const [who, setWho] = useState(TEAM[2].login);
  return html`<div class=${compact ? "stack" : "card"}>
    ${!compact && html`<h2>Practice first</h2>`}
    <p class="small">Try every button and form as a team member. The guide reads the real project, but anything you do is only written to a practice log. Nothing is sent to GitHub, so you cannot make a mistake.</p>
    <div class="row"><div class="field" style="min-width:200px"><label for="pw">Practice as</label>
      <${Select} id="pw" value=${who} onChange=${setWho} options=${TEAM.map((m) => ({ value: m.login, label: m.name }))} /></div>
      <button class="btn" style="align-self:end" onClick=${() => app.startPractice(who)}>Start practising</button></div>
  </div>`;
}

export function Practice() {
  const app = useApp();
  if (!app.practice)
    return html`<section class="page-head"><p class="eyebrow">Safe to try</p><h1>Practice mode</h1></section><${PracticeStart} />`;
  const log = app.gh.log;
  return html`<section class="page-head"><p class="eyebrow">Practising as ${app.member?.name}</p><h1>Practice log</h1>
      <p class="lede">Everything below would have happened on GitHub if you were signed in for real. Nothing was sent. When you are ready, stop practising and sign in.</p></section>
    <div class="row"><button class="btn primary" onClick=${app.signOut}>Stop practising</button><a class="btn" href="#/signin">How to sign in for real</a></div>
    <div class="card">${log.length
      ? html`<div class="tbl"><table><thead><tr><th>When</th><th>What would have happened</th><th>Details</th></tr></thead><tbody>
          ${log.map((e) => html`<tr><td class="num">${e.at.toLocaleTimeString()}</td><td><b>${e.action}</b></td><td class="small">${e.detail}</td></tr>`)}</tbody></table></div>`
      : html`<p class="small muted">Nothing yet. Try ticking a step on a task, posting a comment, creating a task, or sending a document form.</p>`}</div>
    <p class="small muted">In practice mode the guide reads GitHub without a key, which GitHub limits to 60 requests an hour per computer. If pages stop loading, wait a few minutes.</p>`;
}
