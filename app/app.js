// Group 9 Project Guide: entry point, router, and the signed-in member.
import { render } from "./vendor/preact-htm.module.js";
import { Ctx, clearData, forgetKey, html, loadKey, makeGitHub, useEffect, useState } from "./lib/ui.js";
import { explain } from "./lib/github.js";
import { memberByLogin } from "./content/project.js";
import { PracticeGitHub } from "./lib/practice.js";
import { Home } from "./views/home.js";
import { SignIn } from "./views/signin.js";
import { Learn } from "./views/learn.js";
import { Sprints } from "./views/sprints.js";
import { Tasks, TaskDetail } from "./views/tasks.js";
import { NewTask } from "./views/newtask.js";
import { Documents } from "./views/documents.js";
import { Reviews, ReviewDetail } from "./views/reviews.js";
import { Help } from "./views/help.js";
import { Practice } from "./views/practice.js";

const NAV = [
  ["", "Home"],
  ["learn", "Learn"],
  ["sprints", "Sprints"],
  ["tasks", "Tasks"],
  ["new", "New task"],
  ["docs", "Documents"],
  ["reviews", "Reviews"],
  ["help", "Help"],
];

const PRACTICE_KEY = "g9.guide.practice";

function parseHash() {
  const raw = decodeURIComponent(location.hash.replace(/^#\/?/, ""));
  const [path, query = ""] = raw.split("?");
  const parts = path.split("/").filter(Boolean);
  return { parts, query: Object.fromEntries(new URLSearchParams(query)) };
}

function Page({ route }) {
  const [a, b] = route.parts;
  switch (a) {
    case undefined:
      return html`<${Home} />`;
    case "signin":
      return html`<${SignIn} />`;
    case "learn":
      return html`<${Learn} topic=${b} />`;
    case "sprints":
      return html`<${Sprints} />`;
    case "tasks":
      return html`<${Tasks} query=${route.query} />`;
    case "task":
      return html`<${TaskDetail} number=${Number(b)} />`;
    case "new":
      return html`<${NewTask} query=${route.query} />`;
    case "docs":
      return html`<${Documents} form=${b} query=${route.query} />`;
    case "reviews":
      return html`<${Reviews} />`;
    case "review":
      return html`<${ReviewDetail} number=${Number(b)} />`;
    case "help":
      return html`<${Help} />`;
    case "practice":
      return html`<${Practice} />`;
    default:
      return html`<div class="note warn">There is no page called “${a}”. <a href="#/">Go home</a>.</div>`;
  }
}

function App() {
  const [route, setRoute] = useState(parseHash());
  const [session, setSession] = useState(() => {
    // ?practice=<login> in the address, or a practice session started on the sign-in page.
    let login = new URLSearchParams(location.search).get("practice");
    try {
      login = login || sessionStorage.getItem(PRACTICE_KEY);
    } catch {
      // storage blocked
    }
    const member = memberByLogin(login);
    if (member) return { gh: new PracticeGitHub(member), me: null, checking: true };
    return { gh: makeGitHub(loadKey()), me: null, checking: Boolean(loadKey()) };
  });
  const [, setLog] = useState(0);
  session.gh.onChange = () => {
    setLog((n) => n + 1);
    say("Practice: recorded in the practice log. Nothing was sent to GitHub.", { href: "#/practice", text: "See the log" });
  };
  const [version, setVersion] = useState(0);
  const [toast, setToast] = useState(null);

  useEffect(() => {
    const on = () => {
      setRoute(parseHash());
      window.scrollTo(0, 0);
    };
    window.addEventListener("hashchange", on);
    return () => window.removeEventListener("hashchange", on);
  }, []);

  // Confirm a remembered key on load.
  useEffect(() => {
    if (!session.checking) return;
    session.gh
      .whoAmI()
      .then((me) => setSession((s) => ({ ...s, me, checking: false })))
      .catch((e) => {
        forgetKey();
        setSession({ gh: makeGitHub(null), me: null, checking: false });
        say(`Signed out: ${explain(e)}`);
      });
  }, []);

  function say(message, link) {
    setToast({ message, link });
    clearTimeout(say.timer);
    say.timer = setTimeout(() => setToast(null), 6000);
  }

  const app = {
    gh: session.gh,
    me: session.me,
    practice: Boolean(session.gh.practice),
    startPractice(login) {
      const member = memberByLogin(login);
      if (!member) return;
      try {
        sessionStorage.setItem(PRACTICE_KEY, member.login);
      } catch {
        // storage blocked: practice lasts until the page reloads
      }
      const gh = new PracticeGitHub(member);
      gh.whoAmI().then((me) => {
        clearData();
        setSession({ gh, me, checking: false });
        setVersion((v) => v + 1);
        location.hash = "#/";
        say(`Practice mode as ${member.name}: try anything. Nothing is sent to GitHub.`);
      });
    },
    member: memberByLogin(session.me?.login),
    version,
    refresh() {
      session.gh.clearCache();
      clearData();
      setVersion((v) => v + 1);
    },
    signedIn(gh, me) {
      clearData();
      setSession({ gh, me, checking: false });
      setVersion((v) => v + 1);
    },
    signOut() {
      try {
        sessionStorage.removeItem(PRACTICE_KEY);
      } catch {
        // nothing stored
      }
      if (session.gh.practice) {
        setSession({ gh: makeGitHub(loadKey()), me: null, checking: Boolean(loadKey()) });
        clearData();
        setVersion((v) => v + 1);
        say("Practice mode ended. Nothing was sent to GitHub.");
        location.hash = "#/";
        return;
      }
      forgetKey();
      clearData();
      setSession({ gh: makeGitHub(null), me: null, checking: false });
      setVersion((v) => v + 1);
      say("Signed out. Your key is no longer stored in this browser.");
      location.hash = "#/";
    },
    say,
  };

  const here = route.parts[0] || "";
  return html`<${Ctx.Provider} value=${app}>
    <header class="top">
      <div class="top-inner">
        <a class="brand" href="#/"><span class="brand-mark">G9</span><b>Group 9 Project Guide</b></a>
        <div class="who">
          ${session.checking
            ? html`<span class="spinner"></span>`
            : session.me
              ? html`${app.practice && html`<a class="chip waiting" href="#/practice" title="Nothing is sent to GitHub">Practice mode</a>`}<img src=${`${session.me.avatar}&s=52`} alt="" /><span>${app.member?.name || session.me.login}</span>
                  <button class="btn link" onClick=${app.signOut}>${app.practice ? "Stop practice" : "Sign out"}</button>`
              : html`<a class="btn primary" href="#/signin">Sign in</a>`}
        </div>
      </div>
      <nav class="nav" aria-label="Main">
        ${NAV.map(([slug, label]) => {
          const on = slug === here || (slug === "tasks" && here === "task") || (slug === "reviews" && here === "review");
          return html`<a href=${`#/${slug}`} class=${on ? "on" : ""} aria-current=${on ? "page" : undefined}>${label}</a>`;
        })}
      </nav>
    </header>
    <main id="main"><${Page} route=${route} /></main>
    ${toast && html`<div class="toast" role="status">${toast.message} ${toast.link && html`<a href=${toast.link.href} target=${toast.link.external ? "_blank" : undefined} rel="noopener">${toast.link.text}</a>`}</div>`}
  <//>`;
}

const root = document.getElementById("app");
root.textContent = "";
render(html`<${App} />`, root);
