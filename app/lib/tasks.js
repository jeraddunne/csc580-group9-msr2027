// Pure helpers for tasks: checklists in issue text, new-task bodies, branch names.
// No DOM and no network, so app/tests/tasks.test.mjs can test them with Node.

const TASK_LINE = /^(\s*[-*+]\s+)\[( |x|X)\](\s+)(.*)$/;
const FENCE = /^\s*(```|~~~)/;

// Every checklist item ("- [ ] step" or "- [x] step") outside code blocks, in order.
export function parseChecklist(body) {
  const items = [];
  let inFence = false;
  (body || "").split("\n").forEach((raw, line) => {
    const text = raw.replace(/\r$/, "");
    if (FENCE.test(text)) {
      inFence = !inFence;
      return;
    }
    if (inFence) return;
    const m = TASK_LINE.exec(text);
    if (m) items.push({ index: items.length, line, done: m[2].toLowerCase() === "x", text: m[4].trim() });
  });
  return items;
}

// Tick or untick item `index`. `expectedText` guards against the body having changed since
// it was read: if item `index` no longer has that text, nothing is changed and null returns.
export function setChecklistItem(body, index, done, expectedText) {
  const lines = (body || "").split("\n");
  const item = parseChecklist(body)[index];
  if (!item) return null;
  if (expectedText !== undefined && item.text !== expectedText.trim()) return null;
  const cr = lines[item.line].endsWith("\r") ? "\r" : "";
  const m = TASK_LINE.exec(lines[item.line].replace(/\r$/, ""));
  lines[item.line] = `${m[1]}[${done ? "x" : " "}]${m[3]}${m[4]}${cr}`;
  return lines.join("\n");
}

// Links, `code`, and **bold** inside one checklist step, as tokens for safe display
// (the page builds elements from them; step text is never inserted as HTML).
const INLINE = /(`[^`]+`)|\[([^\]]+)\]\(([^)\s]+)\)|\*\*([^*]+)\*\*|(https?:\/\/[^\s)]*[^\s).,;:!?])/g;
export function inlineTokens(text) {
  const out = [];
  let last = 0;
  for (const m of (text || "").matchAll(INLINE)) {
    if (m.index > last) out.push({ type: "text", text: text.slice(last, m.index) });
    if (m[1]) out.push({ type: "code", text: m[1].slice(1, -1) });
    else if (m[2]) out.push(safeLink(m[2], m[3]));
    else if (m[4]) out.push({ type: "bold", text: m[4] });
    else out.push(safeLink(m[5], m[5]));
    last = m.index + m[0].length;
  }
  if (last < (text || "").length) out.push({ type: "text", text: text.slice(last) });
  return out;
}

function safeLink(text, href) {
  return /^https?:\/\//i.test(href) || href.startsWith("#") ? { type: "link", text, href } : { type: "text", text };
}

export function checklistProgress(body) {
  const items = parseChecklist(body);
  return { done: items.filter((i) => i.done).length, total: items.length };
}

// Lower-case words joined by hyphens, at most `max` characters, for branch and file names.
export function slugify(text, max = 40) {
  const slug = (text || "")
    .toLowerCase()
    .normalize("NFKD")
    .replace(/[^a-z0-9]+/g, "-")
    .replace(/^-+|-+$/g, "");
  return slug.slice(0, max).replace(/-+$/g, "") || "change";
}

// The repository's branch convention: <type>/<issue>-<slug> (docs/PROCESS.md).
export function branchName(type, issue, title) {
  const kind = slugify(type || "docs", 20);
  return issue ? `${kind}/${issue}-${slugify(title, 36)}` : `${kind}/${slugify(title, 40)}`;
}

export const TASK_TYPES = ["research", "pipeline", "data", "docs", "test", "process", "report", "presentation"];
export const PRIORITIES = ["High", "Medium", "Low"];

// The same headings as .github/ISSUE_TEMPLATE/10-guided-task.yml, so a task made in the app
// reads like one made from the form and the issue-labeler workflow understands it.
export function guidedTaskBody(t) {
  const steps = (t.steps || []).map((s) => s.trim()).filter(Boolean);
  const numbered = steps.map((s, i) => `- [ ] ${i + 1}. ${s}`).join("\n");
  const section = (heading, value) => `### ${heading}\n\n${(value || "").trim() || "_No response_"}\n`;
  return [
    section("Type", t.type),
    section("Sprint", t.sprint),
    section("Priority", t.priority),
    section("Why this matters", t.why),
    section("Time needed", t.time),
    section("Due", t.due),
    section("What you need before you start", t.need),
    section("Steps", numbered),
    section("Done when", t.doneWhen),
    section(
      "If you get stuck",
      "Comment on this issue in plain words: which step you are on and what you see on screen."
    ),
    "_Created with the Group 9 app._\n",
  ].join("\n");
}

// Problems that stop a task from being created, in plain words; empty when it is ready.
export function taskProblems(t) {
  const problems = [];
  if (!(t.title || "").trim()) problems.push("Give the task a title.");
  if (!TASK_TYPES.includes(t.type)) problems.push("Choose a type.");
  if (!t.sprint) problems.push("Choose a sprint.");
  if (!PRIORITIES.includes(t.priority)) problems.push("Choose a priority.");
  if (!(t.why || "").trim()) problems.push("Say why the task matters.");
  if (!(t.steps || []).some((s) => s.trim())) problems.push("Add at least one step.");
  if (!(t.doneWhen || "").trim()) problems.push("Say how someone can tell it is done.");
  return problems;
}

// Days between two ISO dates (b - a), counting calendar days.
export function daysBetween(a, b) {
  const d = (s) => Date.UTC(+s.slice(0, 4), +s.slice(5, 7) - 1, +s.slice(8, 10));
  return Math.round((d(b) - d(a)) / 86400000);
}

export function isoDate(date = new Date()) {
  const p = (n) => String(n).padStart(2, "0");
  return `${date.getFullYear()}-${p(date.getMonth() + 1)}-${p(date.getDate())}`;
}
