import { html, useApp } from "../lib/ui.js";
import { LINKS, TEAM } from "../content/project.js";

export function Help() {
  const app = useApp();
  return html`<section class="page-head"><p class="eyebrow">Stuck, curious, or careful</p><h1>Help</h1></section>
    <div class="grid two" style="align-items:start">
      <div class="card"><h2>If you are stuck</h2>
        <ol class="small" style="margin:0;padding-left:1.2em;display:grid;gap:6px">
          <li>Open your task and write a comment: which step you are on and what you see on screen. That is always the right move, and it counts as participation.</li>
          <li>To reach someone, type <code>@</code> and their GitHub name in the comment: ${TEAM.map((m) => html`<code>@${m.login}</code> (${m.name}, ${m.role}) `)}.</li>
          <li>Nothing you send can break the project: every change waits for a teammate's review.</li>
        </ol></div>
      <div class="card"><h2>What the guide does on GitHub for you</h2>
        <div class="tbl"><table><thead><tr><th>You press</th><th>On GitHub, under your name</th></tr></thead><tbody>
          <tr><td>Tick a step</td><td>Edits the task's text, turning <code>[ ]</code> into <code>[x]</code></td></tr>
          <tr><td>Post comment</td><td>A comment on the issue</td></tr>
          <tr><td>Take this task / Give it back</td><td>Adds or removes you as assignee</td></tr>
          <tr><td>Board status</td><td>Sets the Status field on the project board</td></tr>
          <tr><td>Mark done</td><td>A “Done: …” comment, then closes the issue</td></tr>
          <tr><td>Create task</td><td>A new issue with labels, sprint, and board fields</td></tr>
          <tr><td>Send (Documents)</td><td>A branch, a commit changing one file, and a pull request asking your chosen reviewer</td></tr>
          <tr><td>Approve / Ask for changes</td><td>A pull request review</td></tr>
        </tbody></table></div></div>
      <div class="card"><h2>Your key</h2>
        <p class="small">Your GitHub key is stored only in this browser${app.me ? "" : " once you sign in"}. The guide sends it only to GitHub. Anyone with the key can act as you on public GitHub projects, so keep it private.</p>
        <ul class="small" style="margin:0;padding-left:1.2em"><li>Sign out removes it from this browser.</li><li>Delete it for good on <a href=${LINKS.keys} target="_blank" rel="noopener">GitHub's key page</a>.</li><li>On a shared computer, untick “Remember me” when you sign in.</li></ul>
        ${app.me && html`<div><button class="btn" onClick=${app.signOut}>Sign out</button></div>`}</div>
      <div class="card"><h2>Other ways in</h2>
        <ul class="small" style="margin:0;padding-left:1.2em;display:grid;gap:4px">
          <li><a href=${LINKS.site} target="_blank" rel="noopener">The documentation website</a>: every document, readable, with search.</li>
          <li><a href=${LINKS.site + "docs/NO_GIT_GUIDE/"} target="_blank" rel="noopener">Working without git</a>: the same actions done directly on github.com.</li>
          <li><a href=${LINKS.board} target="_blank" rel="noopener">The project board</a> and the <a href=${LINKS.repo} target="_blank" rel="noopener">repository</a> on GitHub.</li>
        </ul></div>
    </div>`;
}
