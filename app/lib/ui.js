// Shared UI pieces. Preact + htm, vendored in app/vendor (no build step).
import { html, useState, useEffect, useContext, createContext, useCallback, useMemo, useRef } from "../vendor/preact-htm.module.js";
import { GitHub, explain } from "./github.js";
import { memberByLogin } from "../content/project.js";
import { inlineTokens } from "./tasks.js";

export { html, useState, useEffect, useContext, useCallback, useMemo, useRef };

export const Ctx = createContext(null);
export const useApp = () => useContext(Ctx);

// ---- Sign-in key storage: this browser only ------------------------------------------------
const KEY = "g9.guide.key";
export function loadKey() {
  try {
    return localStorage.getItem(KEY) || sessionStorage.getItem(KEY) || null;
  } catch {
    return null;
  }
}
export function saveKey(token, remember) {
  try {
    (remember ? localStorage : sessionStorage).setItem(KEY, token);
  } catch {
    // Storage blocked (private window): the key lasts for this page only.
  }
}
export function forgetKey() {
  try {
    localStorage.removeItem(KEY);
    sessionStorage.removeItem(KEY);
  } catch {
    // nothing stored
  }
}

// ---- Data hook: load once per key, refresh on demand ---------------------------------------
const memo = new Map();
export function useData(key, loader, deps = []) {
  const app = useApp();
  const cacheKey = `${app.me?.login || "anon"}:${key}:${app.version}`;
  const [state, setState] = useState(() => memo.get(cacheKey) || { loading: true, data: null, error: null });
  useEffect(() => {
    let live = true;
    if (memo.has(cacheKey) && !memo.get(cacheKey).loading) {
      setState(memo.get(cacheKey));
      return undefined;
    }
    setState((s) => ({ ...s, loading: true, error: null }));
    Promise.resolve()
      .then(() => loader(app.gh))
      .then((data) => {
        const next = { loading: false, data, error: null };
        memo.set(cacheKey, next);
        if (live) setState(next);
      })
      .catch((error) => {
        if (live) setState({ loading: false, data: null, error });
      });
    return () => {
      live = false;
    };
  }, [cacheKey, ...deps]);
  return state;
}
export function clearData() {
  memo.clear();
}

export function makeGitHub(token) {
  return new GitHub(token);
}

// ---- Small components ----------------------------------------------------------------------
// One line of text with links, code, and bold shown as such (see inlineTokens).
export function Inline({ text }) {
  return inlineTokens(text).map((t) =>
    t.type === "code"
      ? html`<code>${t.text}</code>`
      : t.type === "bold"
        ? html`<b>${t.text}</b>`
        : t.type === "link"
          ? html`<a href=${t.href} target=${t.href.startsWith("#") ? undefined : "_blank"} rel="noopener" onClick=${(e) => e.stopPropagation()}>${t.text}</a>`
          : t.text
  );
}

export function Loading({ what = "Loading" }) {
  return html`<p class="muted small"><span class="spinner"></span> ${what}…</p>`;
}

export function ErrorNote({ error, retry }) {
  return html`<div class="note bad" role="alert"><b>Something went wrong.</b><span>${explain(error)}</span>
    ${retry && html`<span><button class="btn" onClick=${retry}>Try again</button></span>`}</div>`;
}

export function Loaded({ state, what, children }) {
  if (state.error) return html`<${ErrorNote} error=${state.error} />`;
  if (state.loading && !state.data) return html`<${Loading} what=${what} />`;
  return children(state.data);
}

export const STATUS_CLASS = { Todo: "todo", "In progress": "progress", Done: "done", Block: "block", Cancelled: "cancel" };

export function StatusChip({ status }) {
  const s = status || "Not on board";
  return html`<span class=${`chip ${STATUS_CLASS[s] || "plain"}`}>${s}</span>`;
}

export function Bar({ value, total, good }) {
  const pct = total ? Math.round((100 * value) / total) : 0;
  return html`<div class=${`bar${good ? " good" : ""}`} role="progressbar" aria-valuenow=${pct} aria-valuemin="0" aria-valuemax="100" aria-label=${`${value} of ${total}`}><span style=${`width:${pct}%`}></span></div>`;
}

export function Avatars({ users = [] }) {
  if (!users.length) return html`<span class="muted">nobody yet</span>`;
  return html`<span class="avatars">${users.map((u) => html`<img src=${`${u.avatar_url}&s=40`} alt=${u.login} title=${memberByLogin(u.login)?.name || u.login} />`)}</span>`;
}

export function Labels({ labels = [] }) {
  return labels
    .filter((l) => !/^priority:|^type:/.test(l.name))
    .map((l) => html`<span class="label">${l.name}</span>`);
}

export function Field({ label, hint, children, id }) {
  return html`<div class="field"><label for=${id}>${label}</label>${children}${hint && html`<span class="hint">${hint}</span>`}</div>`;
}

export function Select({ id, value, onChange, options, placeholder }) {
  return html`<select id=${id} value=${value} onChange=${(e) => onChange(e.target.value)}>
    ${placeholder !== undefined && html`<option value="">${placeholder}</option>`}
    ${options.map((o) => (typeof o === "string" ? html`<option value=${o}>${o}</option>` : html`<option value=${o.value}>${o.label}</option>`))}
  </select>`;
}

// GitHub renders and sanitises issue and comment text; this shows that HTML.
export function GitHubHTML({ html: body }) {
  if (!body) return html`<p class="muted small">No description.</p>`;
  return html`<div class="md" dangerouslySetInnerHTML=${{ __html: body }}></div>`;
}

export function when(iso) {
  if (!iso) return "";
  const d = new Date(iso);
  return d.toLocaleDateString(undefined, { month: "short", day: "numeric" });
}

export function RequireSignIn({ children, what = "do this" }) {
  const app = useApp();
  if (app.me) return children;
  return html`<div class="note info"><b>Sign in to ${what}.</b><span>Signing in lets the guide save your work on GitHub under your own name.</span>
    <span><a class="btn primary" href="#/signin">Sign in</a></span></div>`;
}
