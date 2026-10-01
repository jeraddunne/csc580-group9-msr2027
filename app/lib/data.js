// Loaders shared by the pages. Each takes the GitHub client and returns plain data.
import { parseCSV } from "./csv.js";
import { LINKS } from "../content/project.js";

export async function loadProject(gh) {
  const [issues, milestones] = await Promise.all([gh.issues({ state: "all" }), gh.milestones()]);
  let board = new Map();
  let boardError = null;
  if (gh.token) {
    try {
      board = await gh.boardStatuses();
    } catch (e) {
      boardError = e;
    }
  }
  return { issues, milestones, board, boardError };
}

// Board status when the issue is on the board; otherwise Done for closed and Todo for open.
export function statusOf(issue, board) {
  const s = board?.get(issue.number)?.status;
  if (s) return s;
  return issue.state === "closed" ? "Done" : "Todo";
}

export function milestoneByTitle(milestones, title) {
  return milestones.find((m) => m.title === title) || null;
}

// A results table: from the site (results/ sits next to app/), else from GitHub.
const tables = new Map();
export async function resultsTable(name) {
  if (tables.has(name)) return tables.get(name);
  const tryFetch = async (url) => {
    const res = await fetch(url);
    if (!res.ok) throw new Error(`${name}: ${res.status}`);
    return res.text();
  };
  let text;
  try {
    text = await tryFetch(new URL(`../results/${name}`, location.href).href);
  } catch {
    text = await tryFetch(LINKS.raw(`results/${name}`));
  }
  const rows = parseCSV(text);
  tables.set(name, rows);
  return rows;
}

export async function rawFile(path) {
  const res = await fetch(LINKS.raw(path), { cache: "no-store" });
  if (!res.ok) throw new Error(`${path}: ${res.status}`);
  return res.text();
}
