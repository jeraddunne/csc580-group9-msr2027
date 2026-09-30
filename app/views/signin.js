import { html, useApp, useState, makeGitHub, saveKey } from "../lib/ui.js";
import { explain } from "../lib/github.js";
import { LINKS, memberByLogin } from "../content/project.js";
import { PracticeStart } from "./practice.js";

export function SignIn() {
  const app = useApp();
  const [token, setToken] = useState("");
  const [remember, setRemember] = useState(true);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState(null);
  const [result, setResult] = useState(null);

  async function check(e) {
    e.preventDefault();
    const key = token.trim();
    if (!key) return;
    setBusy(true);
    setError(null);
    try {
      const gh = makeGitHub(key);
      const me = await gh.whoAmI();
      let board = false;
      try {
        await gh.board();
        board = true;
      } catch {
        board = false;
      }
      saveKey(key, remember);
      setResult({ me, board });
      app.signedIn(gh, me);
      setToken("");
    } catch (err) {
      setError(explain(err));
    } finally {
      setBusy(false);
    }
  }

  if (app.me && result) {
    const m = memberByLogin(result.me.login);
    return html`<section class="page-head"><p class="eyebrow">Signed in</p><h1>Welcome, ${m?.name || result.me.login}</h1></section>
      <div class="card">
        <ul class="stack" style="list-style:none;margin:0;padding:0">
          <li>${result.me.canWrite ? "✓" : "✗"} ${result.me.canWrite ? "You can make changes in the project." : "You cannot make changes yet: accept the repository invitation first."}</li>
          <li>${result.board ? "✓" : "–"} ${result.board ? "You can move tasks on the board." : "Board changes are off: your key is missing the project box. Everything else works."}</li>
          <li>${m ? "✓" : "–"} ${m ? `You are listed as ${m.role}.` : "Your GitHub name is not in the team list; you can still use the guide."}</li>
        </ul>
        ${!result.me.canWrite && html`<p><a class="btn" href=${LINKS.invitation} target="_blank" rel="noopener">Open the invitation</a></p>`}
        <div class="row"><a class="btn primary" href="#/">Go to my home page</a><a class="btn" href="#/learn">Start with Learn</a></div>
      </div>`;
  }

  if (app.me && app.practice) {
    return html`<section class="page-head"><h1>You are practising</h1><p class="lede">Stop practising first, then sign in with your key.</p></section>
      <div class="row"><button class="btn primary" onClick=${app.signOut}>Stop practising</button></div>`;
  }

  if (app.me) {
    return html`<section class="page-head"><h1>You are signed in</h1><p class="lede">As ${app.member?.name || app.me.login}. To use a different key, sign out first.</p></section>
      <div class="row"><a class="btn primary" href="#/">Home</a><button class="btn" onClick=${app.signOut}>Sign out</button></div>`;
  }

  return html`<section class="page-head">
      <p class="eyebrow">One time, about 3 minutes</p>
      <h1>Sign in with your GitHub key</h1>
      <p class="lede">The guide saves what you do on GitHub under your own name, so it counts as your work. To do that it needs a key from your GitHub account. You make the key once; this browser remembers it.</p>
    </section>
    <div class="grid two">
      <div class="card">
        <h2>Make your key</h2>
        <ol class="stack" style="margin:0;padding-left:1.2em">
          <li><b>Accept the invitation</b> to the project, if you have not yet: <a href=${LINKS.invitation} target="_blank" rel="noopener">open the invitation</a>.</li>
          <li><b>Open the key page</b>: <a href=${LINKS.newKey} target="_blank" rel="noopener">make a key for the guide</a>. GitHub may ask for your password. The page is already filled in: the note says “Group 9 Project Guide” and two boxes are ticked, <code>public_repo</code> and <code>project</code>.</li>
          <li><b>Expiration</b>: choose <i>Custom</i> and pick <b>Dec 31, 2026</b>, so it lasts the whole course.</li>
          <li>Scroll to the bottom and click <b>Generate token</b>.</li>
          <li><b>Copy</b> the key that starts with <code>ghp_</code>. GitHub shows it only once.</li>
        </ol>
        <div class="note warn small"><b>Keep your key private.</b><span>It lets the guide act as you on public GitHub projects. Do not paste it into chat or email. You can delete it any time on <a href=${LINKS.keys} target="_blank" rel="noopener">GitHub's key page</a>; the guide then stops working until you make a new one.</span></div>
      </div>
      <form class="card form" onSubmit=${check}>
        <h2>Paste your key</h2>
        <div class="field">
          <label for="key">Your GitHub key</label>
          <input id="key" type="password" autocomplete="off" spellcheck="false" placeholder="ghp_…" value=${token} onInput=${(e) => setToken(e.target.value)} />
        </div>
        <label class="check"><input type="checkbox" checked=${remember} onChange=${(e) => setRemember(e.target.checked)} /><span>Remember me on this computer. Untick on a shared computer: the key is then forgotten when you close the tab.</span></label>
        ${error && html`<div class="note bad" role="alert">${error}</div>`}
        <div class="row"><button class="btn primary" disabled=${busy || !token.trim()}>${busy ? html`<span class="spinner"></span> Checking` : "Sign in"}</button>
          <a class="btn link" href="#/learn">Look around first, without signing in</a></div>
        <p class="tiny muted">The key stays in this browser. The guide sends it only to GitHub (api.github.com), with each request.</p>
      </form>
    </div>
    <${PracticeStart} />`;
}
