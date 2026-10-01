// Document forms: each function takes a file's current text and the form's answers and
// returns the new text, or throws an Error whose message is shown to the member.
// Pure (no DOM, no network); app/tests/docs.test.mjs runs them on the real files.

const cell = (s) => String(s ?? "").replace(/\|/g, "/").replace(/\r?\n/g, " ").trim();

function eol(text) {
  return text.includes("\r\n") ? "\r\n" : "\n";
}

// The member's row in TEAM_CHARTER.md section 14 (not the team table at the top), or null.
export function charterRow(text, memberName) {
  const lines = text.split(/\r?\n/);
  const start = lines.findIndex((l) => /^##\s+14\.\s+Signatures/.test(l));
  if (start < 0) return null;
  const name = memberName.trim().toLowerCase();
  for (let i = start + 1; i < lines.length && !/^##\s/.test(lines[i]); i += 1) {
    const cells = lines[i].split("|").map((c) => c.trim());
    if (cells.length >= 4 && cells[1].toLowerCase() === name) {
      return { line: lines[i], date: cells[2], signed: /^\d{4}-\d{2}-\d{2}$/.test(cells[2]) };
    }
  }
  return null;
}

// TEAM_CHARTER.md section 14: fill the member's own row with the date and a reference.
export function signCharter(text, memberName, date, reference) {
  const nl = eol(text);
  const lines = text.split(/\r?\n/);
  const start = lines.findIndex((l) => /^##\s+14\.\s+Signatures/.test(l));
  if (start < 0) throw new Error("Could not find section 14, Signatures, in TEAM_CHARTER.md.");
  const name = memberName.trim().toLowerCase();
  for (let i = start + 1; i < lines.length && !/^##\s/.test(lines[i]); i += 1) {
    const cells = lines[i].split("|").map((c) => c.trim());
    if (cells.length < 4 || cells[1].toLowerCase() !== name) continue;
    if (/^\d{4}-\d{2}-\d{2}$/.test(cells[2])) {
      throw new Error(`${memberName} already signed on ${cells[2]}.`);
    }
    lines[i] = `| ${cells[1]} | ${cell(date)} | ${cell(reference)} |`;
    return lines.join(nl);
  }
  throw new Error(`There is no row for ${memberName} in section 14 of the charter.`);
}

export const PROFILE_FIELDS = [
  "Pronouns (optional)",
  "Time zone",
  "Hours per week for this project",
  "Best meeting times",
  "Days that never work",
  "Known absences",
];

// docs/team/<name>.md: set table fields, bullet sections, role preferences, and notes.
// Only fields with a non-empty answer change; everything else stays as it is.
export function updateProfile(text, answers) {
  const nl = eol(text);
  let lines = text.split(/\r?\n/);
  const setRow = (label, value) => {
    if (!cell(value)) return;
    const i = lines.findIndex((l) => l.split("|")[1]?.trim() === label);
    if (i >= 0) lines[i] = `| ${label} | ${cell(value)} |`;
  };
  for (const f of PROFILE_FIELDS) setRow(f, answers[f]);
  for (const sprint of ["Sprint 1", "Sprint 2", "Sprint 3"]) setRow(sprint, answers[`Role preference ${sprint}`]);

  const replaceSection = (heading, bodyLines) => {
    const i = lines.findIndex((l) => l.trim() === `## ${heading}`);
    if (i < 0 || bodyLines.length === 0) return;
    let j = i + 1;
    while (j < lines.length && !/^##\s/.test(lines[j])) j += 1;
    lines = [...lines.slice(0, i + 1), "", ...bodyLines, "", ...lines.slice(j)];
  };
  const bullets = (value) =>
    (value || "")
      .split(/\r?\n/)
      .map((s) => s.replace(/^\s*[-*]\s*/, "").trim())
      .filter(Boolean)
      .map((s) => `- ${s}`);
  replaceSection("Strengths I bring", bullets(answers.strengths));
  replaceSection("What I want to learn", bullets(answers.learn));
  const notes = (answers.workingStyle || "").trim();
  replaceSection("Working style notes", notes ? notes.split(/\r?\n/) : []);
  return lines.join(nl);
}

// A new docs/meeting-notes/YYYY-MM-DD-<type>.md from the meeting template's structure.
export function meetingNote(m) {
  const attendees = ["Leticia Aderhold", "Jerad Dunne", "Allie Hodges", "Hina Kramer", "Instructor (if present)"]
    .map((n) => `[${(m.attendees || []).includes(n) ? "x" : " "}] ${n}`)
    .join(" ");
  const bullets = (v) =>
    (v || "")
      .split(/\r?\n/)
      .map((s) => s.trim())
      .filter(Boolean)
      .map((s) => `- ${s.replace(/^[-*]\s*/, "")}`)
      .join("\n") || "-";
  const agenda =
    (m.agenda || "")
      .split(/\r?\n/)
      .map((s) => s.trim())
      .filter(Boolean)
      .map((s, i) => `${i + 1}. ${s.replace(/^\d+\.\s*/, "")}`)
      .join("\n") || "1.";
  const decisions = (m.decisions || []).filter((d) => cell(d.decision));
  const actions = (m.actions || []).filter((a) => cell(a.action));
  const title = m.type.charAt(0).toUpperCase() + m.type.slice(1);
  return [
    `# ${title} meeting ${m.date}`,
    "",
    `- Type: ${m.type}`,
    `- Date and time: ${cell(m.date)} ${cell(m.time)}`.trimEnd(),
    "- Location or call link (no personal details): " + cell(m.location),
    `- Facilitator: ${cell(m.facilitator)}`,
    `- Note taker: ${cell(m.noteTaker)}`,
    `- Attendees: ${attendees}`,
    `- Related sprint document: ${cell(m.sprintDoc) || "none"}`,
    "",
    "## Agenda",
    "",
    agenda,
    "",
    "## Notes",
    "",
    bullets(m.notes),
    "",
    "## Decisions",
    "",
    "| # | Decision | Rationale | Needs an ADR? | ADR file |",
    "|---|---|---|---|---|",
    ...(decisions.length
      ? decisions.map((d, i) => `| ${i + 1} | ${cell(d.decision)} | ${cell(d.rationale)} | ${d.adr ? "yes" : "no"} | |`)
      : ["| 1 | none | | no | |"]),
    "",
    "## Action items",
    "",
    "| Action | Owner | Due | Issue # | Status |",
    "|---|---|---|---|---|",
    ...(actions.length
      ? actions.map((a) => `| ${cell(a.action)} | ${cell(a.owner)} | ${cell(a.due)} | ${cell(a.issue)} | open |`)
      : ["| none | | | | |"]),
    "",
    "## Parking lot",
    "",
    bullets(m.parking),
    "",
  ].join("\n");
}

export function meetingNotePath(date, type) {
  if (!/^\d{4}-\d{2}-\d{2}$/.test(date)) throw new Error("Use a date like 2026-10-01.");
  return `docs/meeting-notes/${date}-${type}.md`;
}

// The report from scripts/fresh_run_check.py (windows/2-run-pipeline.bat), with the name filled.
export function freshRunRecord(report, memberName) {
  if (!/^#\s*Fresh-run check/m.test(report || "")) {
    throw new Error("Paste the whole report: it starts with '# Fresh-run check'.");
  }
  return report.replace(/YOUR NAME/g, cell(memberName)).replace(/\s*$/, "\n");
}

export function freshRunPath(date, login) {
  return `docs/lean-six-sigma/metrics/fresh-run-${date}-${login.toLowerCase()}.md`;
}

// ai-use-log.md: one new row at the end of the table.
export function appendAiUseRow(text, row) {
  const nl = eol(text);
  const required = ["date", "member", "tool", "what", "where", "verifiedBy", "how"];
  const missing = required.filter((k) => !cell(row[k]));
  if (missing.length) throw new Error("Fill in every field of the AI-use entry.");
  const line = `| ${required.map((k) => cell(row[k])).join(" | ")} |`;
  const body = text.replace(/(\r?\n)*$/, "");
  return `${body}${nl}${line}${nl}`;
}
