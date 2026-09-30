// Document forms, run on the repository's real files so a format change breaks a test.
import { test } from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import {
  appendAiUseRow,
  charterRow,
  freshRunPath,
  freshRunRecord,
  meetingNote,
  meetingNotePath,
  signCharter,
  updateProfile,
} from "../lib/docs.js";
import { parseCSV } from "../lib/csv.js";

const repo = (p) => readFileSync(new URL(`../../${p}`, import.meta.url), "utf8");
// Line-ending independent: a Windows checkout has CRLF, CI has LF.
const lf = (s) => s.replace(/\r\n/g, "\n");

test("signCharter fills only the member's own row in section 14", () => {
  const before = repo("TEAM_CHARTER.md");
  const after = signCharter(before, "Allie Hodges", "2026-10-02", "#51");
  const changed = after.split(/\r?\n/).filter((l, i) => l !== before.split(/\r?\n/)[i]);
  assert.deepEqual(changed, ["| Allie Hodges | 2026-10-02 | #51 |"]);
});

test("charterRow reads section 14, not the team table at the top of the charter", () => {
  const text = repo("TEAM_CHARTER.md");
  assert.equal(charterRow(text, "Jerad Dunne").signed, true);
  assert.equal(charterRow(text, "Allie Hodges").signed, false);
  assert.ok(!charterRow(text, "Allie Hodges").line.includes("@AllieHgs"), "the team table row has the GitHub handle");
  assert.equal(charterRow(text, "Nobody Here"), null);
});

test("signCharter refuses a second signature and an unknown name", () => {
  const before = repo("TEAM_CHARTER.md");
  assert.throws(() => signCharter(before, "Jerad Dunne", "2026-10-02", "#1"), /already signed/);
  assert.throws(() => signCharter(before, "Nobody Here", "2026-10-02", "#1"), /no row/);
});

test("updateProfile fills table fields and sections and leaves the rest alone", () => {
  const before = repo("docs/team/allie-hodges.md");
  const after = lf(updateProfile(before, {
    "Time zone": "Eastern",
    "Hours per week for this project": "6",
    "Role preference Sprint 2": "Scrum Master",
    strengths: "Writing\n- Statistics",
    learn: "",
    workingStyle: "Mornings work best.",
  }));
  assert.ok(after.includes("| Time zone | Eastern |"));
  assert.ok(after.includes("| Hours per week for this project | 6 |"));
  assert.ok(after.includes("| Sprint 2 | Scrum Master |"));
  assert.ok(after.includes("## Strengths I bring\n\n- Writing\n- Statistics\n\n## What I want to learn"));
  assert.ok(after.includes("## What I want to learn\n\n-\n"), "an empty answer leaves the section as it was");
  assert.ok(after.includes("## Working style notes\n\nMornings work best.\n"));
  assert.ok(after.includes("| GitHub | @AllieHgs |"));
  assert.ok(after.includes("| Known absences | |"), "unanswered fields stay empty");
});

test("meetingNote writes a complete note in the template's structure", () => {
  const text = meetingNote({
    type: "checkin",
    date: "2026-10-01",
    time: "18:00",
    facilitator: "Leticia Aderhold",
    noteTaker: "Allie Hodges",
    attendees: ["Leticia Aderhold", "Allie Hodges"],
    agenda: "Board walk\nRisks",
    notes: "Pipeline reproduced | on Linux",
    decisions: [{ decision: "Keep the sample", rationale: "ADR-0007", adr: true }],
    actions: [{ action: "Sign charter", owner: "Hina Kramer", due: "2026-10-05", issue: "#52" }],
  });
  assert.ok(text.startsWith("# Checkin meeting 2026-10-01\n"));
  assert.ok(text.includes("[x] Leticia Aderhold [ ] Jerad Dunne [x] Allie Hodges"));
  assert.ok(text.includes("1. Board walk\n2. Risks"));
  assert.ok(text.includes("- Pipeline reproduced | on Linux"), "notes are bullets, so a | is kept");
  assert.ok(text.includes("| 1 | Keep the sample | ADR-0007 | yes | |"));
  assert.ok(text.includes("| Sign charter | Hina Kramer | 2026-10-05 | #52 | open |"));
  for (const h of ["## Agenda", "## Notes", "## Decisions", "## Action items", "## Parking lot"]) {
    assert.ok(text.includes(h), h);
  }
  assert.equal(meetingNotePath("2026-10-01", "checkin"), "docs/meeting-notes/2026-10-01-checkin.md");
  assert.throws(() => meetingNotePath("Oct 1", "checkin"));
});

test("freshRunRecord fills the name and rejects text that is not a report", () => {
  const report = "# Fresh-run check\n\n| Who and environment | YOUR NAME; Windows |\n";
  assert.ok(freshRunRecord(report, "Hina Kramer").includes("| Who and environment | Hina Kramer; Windows |"));
  assert.throws(() => freshRunRecord("hello", "Hina Kramer"), /whole report/);
  assert.equal(freshRunPath("2026-10-02", "HinaK786"), "docs/lean-six-sigma/metrics/fresh-run-2026-10-02-hinak786.md");
});

test("appendAiUseRow adds exactly one row with seven cells at the end of the log", () => {
  const before = repo("ai-use-log.md");
  const row = {
    date: "2026-10-02",
    member: "Allie Hodges",
    tool: "ChatGPT",
    what: "Drafted meeting notes | tidied",
    where: "docs/meeting-notes/2026-10-01-checkin.md",
    verifiedBy: "Allie Hodges",
    how: "Read against the recording",
  };
  const after = appendAiUseRow(before, row);
  const last = after.trimEnd().split(/\r?\n/).pop();
  assert.equal(last.split("|").length - 2, 7);
  assert.ok(last.includes("Drafted meeting notes / tidied"));
  assert.ok(after.startsWith(before.trimEnd()));
  assert.throws(() => appendAiUseRow(before, { ...row, how: " " }), /every field/);
});

test("parseCSV reads the committed results, including quoted fields", () => {
  const rows = parseCSV(repo("results/rq2_negbin.csv"));
  const hr = rows.find((r) => r.term === "high_risk");
  assert.ok(Math.abs(Number(hr.irr) - 1.411) < 0.001);
  assert.ok(hr.note.includes("NB2"), "the note column contains commas inside quotes");
  assert.deepEqual(parseCSV('a,b\r\n"x, ""y""",2\r\n'), [{ a: 'x, "y"', b: "2" }]);
});
