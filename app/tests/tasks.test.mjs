import { test } from "node:test";
import assert from "node:assert/strict";
import {
  branchName,
  checklistProgress,
  daysBetween,
  guidedTaskBody,
  inlineTokens,
  parseChecklist,
  setChecklistItem,
  slugify,
  taskProblems,
} from "../lib/tasks.js";

const body = [
  "### Steps",
  "",
  "- [ ] 1. Open the file",
  "- [x] 2. Click the pencil",
  "```",
  "- [ ] not a step: inside a code block",
  "```",
  "* [X] 3. Commit",
  "- [ ]no space means not a checkbox",
].join("\n");

test("parseChecklist finds steps outside code blocks, in order", () => {
  const items = parseChecklist(body);
  assert.deepEqual(
    items.map((i) => [i.text, i.done]),
    [
      ["1. Open the file", false],
      ["2. Click the pencil", true],
      ["3. Commit", true],
    ]
  );
  assert.deepEqual(checklistProgress(body), { done: 2, total: 3 });
});

test("setChecklistItem ticks one step and keeps every other line", () => {
  const next = setChecklistItem(body, 0, true, "1. Open the file");
  assert.equal(next.split("\n")[2], "- [x] 1. Open the file");
  assert.equal(next.split("\n").length, body.split("\n").length);
  assert.equal(setChecklistItem(next, 2, false).split("\n")[7], "* [ ] 3. Commit");
});

test("setChecklistItem refuses when the step's text changed meanwhile", () => {
  assert.equal(setChecklistItem(body, 0, true, "1. Something else"), null);
  assert.equal(setChecklistItem(body, 9, true), null);
});

test("setChecklistItem keeps Windows line endings", () => {
  const crlf = "- [ ] a\r\n- [ ] b\r\n";
  assert.equal(setChecklistItem(crlf, 1, true), "- [ ] a\r\n- [x] b\r\n");
});

test("branch names follow <type>/<issue>-<slug>", () => {
  assert.equal(branchName("process", 51, "Sign the team charter (Allie)"), "process/51-sign-the-team-charter-allie");
  assert.equal(branchName("docs", null, "Meeting notes 2026-10-01"), "docs/meeting-notes-2026-10-01");
  assert.equal(slugify("   "), "change");
  assert.ok(slugify("x".repeat(100)).length <= 40);
});

test("a new task has the guided-task headings and numbered checkboxes", () => {
  const t = {
    title: "Review PR #72",
    type: "process",
    sprint: "Sprint 1",
    priority: "High",
    why: "Every member reviews a merged PR in Sprint 1.",
    time: "15 minutes",
    due: "2026-10-05",
    need: "",
    steps: ["Open the PR", " ", "Approve with what you checked"],
    doneWhen: "Your review is on the PR.",
  };
  assert.deepEqual(taskProblems(t), []);
  const text = guidedTaskBody(t);
  for (const h of ["### Type", "### Sprint", "### Priority", "### Why this matters", "### Steps", "### Done when"]) {
    assert.ok(text.includes(h), h);
  }
  assert.ok(text.includes("- [ ] 1. Open the PR\n- [ ] 2. Approve with what you checked"));
  assert.ok(text.includes("### What you need before you start\n\n_No response_"));
  assert.equal(parseChecklist(text).length, 2);
});

test("taskProblems names each missing answer in plain words", () => {
  const problems = taskProblems({ steps: [] });
  assert.ok(problems.includes("Give the task a title."));
  assert.ok(problems.includes("Add at least one step."));
  assert.equal(problems.length, 7);
});

test("inlineTokens finds links, code, and bold, and refuses unsafe links", () => {
  const t = inlineTokens("Run `make setup` using [the guide](https://x.io/g) and **then** see https://y.io/z.");
  assert.deepEqual(
    t.map((x) => x.type),
    ["text", "code", "text", "link", "text", "bold", "text", "link", "text"]
  );
  assert.equal(t[3].href, "https://x.io/g");
  assert.equal(t[7].href, "https://y.io/z", "a full stop after a link is not part of it");
  assert.deepEqual(inlineTokens("[click](javascript:alert(1))")[0].type, "text");
  assert.deepEqual(inlineTokens("plain"), [{ type: "text", text: "plain" }]);
});

test("daysBetween counts calendar days", () => {
  assert.equal(daysBetween("2026-09-17", "2026-10-07"), 20);
  assert.equal(daysBetween("2026-09-30", "2026-09-30"), 0);
});
