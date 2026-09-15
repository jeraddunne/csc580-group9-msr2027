"""Local labelling page and CSV import for the P-01 validation kit.

`python scripts/annotation_kit.py ui --rater jd --round 1` writes one self-contained HTML
file per label kind into data/annotations/work/ (gitignored). The page shows each reading
packet as plain text, keeps labels in the browser's local storage, and downloads a CSV in
the exact label-file format. `python scripts/annotation_kit.py import <csv>` validates that
download and writes it to data/annotations/.

Safety: packet text is inserted with textContent only, so nothing from the dataset is
rendered as HTML or executed. The page makes no network requests.
"""

from __future__ import annotations

import html
import json
import re
from pathlib import Path

import pandas as pd

from . import validation as v

_SIGNAL_SHA = re.compile(r"^- file_sha: `([^`\s]+)`", re.M)
_PAIR_A = re.compile(r"^- file_sha_a: `([^`\s]+)`", re.M)
_PAIR_B = re.compile(r"^- file_sha_b: `([^`\s]+)`", re.M)
_LABEL_FILE = re.compile(r"^(signals|lineage|drift)_([a-z0-9][a-z0-9-]*)_r(\d+)\.csv$")
_DOWNLOAD_SUFFIX = re.compile(r"\s*\(\d+\)(?=\.csv$)")

# Short reminders shown next to each choice. docs/validation/ANNOTATION_GUIDELINE.md is
# the authoritative definition; these summaries must not contradict it.
LABEL_HELP = {
    "RISKY": "Capability is present and would act with the user's permissions in context.",
    "BENIGN_CONTEXT": "Capability is present but only described, warned against, or sandboxed.",
    "NOT_PRESENT": "The rule matched text that does not grant the capability.",
    "MISSED_RISKY": "No rule matched, but a high-risk capability is present. Pick the category.",
    "NONE_PRESENT": "No high-risk capability is present.",
    "YES": "The two variants are the same skill with a shared origin.",
    "NO": "Different skills that happen to share a name.",
    "UNSURE": "Cannot tell from the diff.",
    "TEMPLATE_UPDATE": "The difference comes from a newer or older version of a shared template.",
    "LOCAL_ADAPTATION": "Project-specific edits that change a capability as a side effect.",
    "HARDENING": "The change removes or restricts a risky capability.",
    "CAPABILITY_ADDITION": "The change adds a risky capability.",
    "UNRELATED": "The pair is not the same skill.",
}


def packet_key(kind: str, text: str) -> str | None:
    """Item key from a reading packet: file_sha for signals, 'a|b' for pairs."""
    if kind == "signals":
        m = _SIGNAL_SHA.search(text)
        return m.group(1) if m else None
    a, b = _PAIR_A.search(text), _PAIR_B.search(text)
    return f"{a.group(1)}|{b.group(1)}" if a and b else None


def read_packets(packet_dir: Path, kind: str) -> list[tuple[str, str]]:
    """(key, text) for every packet in a packet directory, in file order."""
    out: list[tuple[str, str]] = []
    if not packet_dir.exists():
        return out
    for path in sorted(packet_dir.glob("*.md")):
        if path.name == "INDEX.md":
            continue
        text = path.read_text(encoding="utf-8")
        key = packet_key(kind, text)
        if key:
            out.append((key, text))
    return out


def build_items(kind: str, labels: pd.DataFrame, packets: list[tuple[str, str]]) -> list[dict]:
    """Group label rows under their reading packet. Every label row appears exactly once."""
    label_col = v.KIND_LABEL_COLUMN[kind]
    labels = labels.fillna("").astype(str)
    missing_packet = "Reading packet not found. Run `annotation_kit.py sheet` for this round."
    items: list[dict] = []
    if kind == "signals":
        order: list[str] = []
        grouped: dict[str, list[dict]] = {}
        for rec in labels.to_dict("records"):
            if rec["file_sha"] not in grouped:
                grouped[rec["file_sha"]] = []
                order.append(rec["file_sha"])
            grouped[rec["file_sha"]].append(
                {
                    "rule_id": rec["rule_id"],
                    "label": rec[label_col],
                    "missed_category": rec.get("missed_category", ""),
                    "notes": rec.get("notes", ""),
                }
            )
        texts = dict(packets)
        seen: set[str] = set()
        for key, _ in packets:
            if key in grouped and key not in seen:
                items.append({"key": key, "packet": texts[key], "rows": grouped[key]})
                seen.add(key)
        for key in order:
            if key not in seen:
                items.append({"key": key, "packet": missing_packet, "rows": grouped[key]})
        return items

    index: dict[str, dict] = {}
    order = []
    for rec in labels.to_dict("records"):
        key = f"{rec['file_sha_a']}|{rec['file_sha_b']}"
        index[key] = rec
        order.append(key)
    texts = dict(packets)
    keys = [k for k, _ in packets if k in index] + [k for k in order if k not in texts]
    for key in dict.fromkeys(keys):
        rec = index[key]
        items.append(
            {
                "key": key,
                "packet": texts.get(key, missing_packet),
                "rows": [
                    {
                        "file_sha_a": rec["file_sha_a"],
                        "file_sha_b": rec["file_sha_b"],
                        "label": rec[label_col],
                        "notes": rec.get("notes", ""),
                    }
                ],
            }
        )
    return items


def build_html(kind: str, rater: str, round_: int, items: list[dict], categories: list[str]) -> str:
    """Render the self-contained labelling page."""
    data = {
        "kind": kind,
        "rater": rater,
        "round": round_,
        "filename": v.label_filename(kind, rater, round_),
        "columns": v.KIND_COLUMNS[kind],
        "labelColumn": v.KIND_LABEL_COLUMN[kind],
        "noneRule": v.NONE_RULE,
        "choices": {
            "rule": list(v.SIGNAL_LABELS),
            "none": list(v.NO_SIGNAL_LABELS),
            "pair": list(v.LINEAGE_LABELS if kind == "lineage" else v.DRIFT_LABELS),
        },
        "help": LABEL_HELP,
        "categories": list(categories),
        "items": items,
    }
    # Escaping every "<" as a JSON unicode escape keeps packet text such as "</script>" or "<!--"
    # interacting with the HTML parser; JSON and JavaScript both decode it back to "<".
    payload = json.dumps(data, ensure_ascii=False).replace("<", "\\u003c")
    title = html.escape(f"P-01 labelling: {kind}, rater {rater}, round {round_}")
    return _TEMPLATE.replace("__TITLE__", title).replace("__DATA__", payload)


def import_labels(
    src: Path,
    target_dir: Path,
    rule_ids: list[str],
    categories: list[str],
    replace: bool = False,
) -> tuple[Path | None, list[str], int]:
    """Validate a downloaded label CSV and write it to the annotations folder.

    Returns (target path or None, problems, labelled row count). Nothing is written when
    there are problems. Existing non-empty labels that differ are only replaced with
    ``replace=True``.
    """
    name = _DOWNLOAD_SUFFIX.sub("", src.name)
    m = _LABEL_FILE.match(name)
    if not m:
        return None, [f"{src.name}: name must look like signals_jd_r1.csv"], 0
    kind, rater, round_ = m.group(1), m.group(2), int(m.group(3))
    df = pd.read_csv(src, dtype=str, keep_default_na=False)
    problems = v.validate_labels(df, kind, rule_ids=rule_ids, categories=categories, source=name)
    if problems:
        return None, problems, 0
    keys = v.KIND_KEYS[kind]
    label_col = v.KIND_LABEL_COLUMN[kind]
    target = target_dir / v.label_filename(kind, rater, round_)
    if target.exists():
        current = pd.read_csv(target, dtype=str, keep_default_na=False)
        cur_keys = set(map(tuple, current[keys].to_numpy().tolist()))
        new_keys = set(map(tuple, df[keys].to_numpy().tolist()))
        if cur_keys != new_keys:
            return None, [f"{name}: rows do not match {target.name}; re-download from the page"], 0
        merged = current.merge(df[[*keys, label_col]], on=keys, suffixes=("_old", "_new"))
        clash = merged[
            (merged[f"{label_col}_old"] != "")
            & (merged[f"{label_col}_new"] != merged[f"{label_col}_old"])
        ]
        if len(clash) and not replace:
            return (
                None,
                [
                    f"{name}: {len(clash)} labels differ from {target.name}; "
                    "re-run with --replace to overwrite them"
                ],
                0,
            )
    target_dir.mkdir(parents=True, exist_ok=True)
    df[v.KIND_COLUMNS[kind]].to_csv(target, index=False)
    return target, [], int((df[label_col].str.strip() != "").sum())


_TEMPLATE = r"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>__TITLE__</title>
<style>
:root { --bg:#f6f6f3; --fg:#1d1d1b; --muted:#66665f; --card:#ffffff; --line:#d8d8d2;
  --accent:#1f5f8b; --accent-fg:#ffffff; --risky:#a1261e; --ok:#2e7d32; --warn:#8a6100; --sel:#e6eef5; }
@media (prefers-color-scheme: dark) {
  :root { --bg:#151514; --fg:#ecece7; --muted:#a4a49c; --card:#1f1f1d; --line:#3b3b37;
    --accent:#7fb3d9; --accent-fg:#101010; --risky:#f0877e; --ok:#80c784; --warn:#e2c160; --sel:#233340; }
}
* { box-sizing: border-box; }
body { margin: 0; background: var(--bg); color: var(--fg);
  font: 15px/1.45 system-ui, -apple-system, "Segoe UI", sans-serif; }
header { position: sticky; top: 0; z-index: 2; background: var(--card);
  border-bottom: 1px solid var(--line); padding: 10px 16px;
  display: flex; flex-wrap: wrap; gap: 8px 16px; align-items: center; }
header h1 { font-size: 16px; margin: 0; }
.progress { flex: 1 1 200px; min-width: 160px; }
.bar { height: 6px; background: var(--line); border-radius: 3px; overflow: hidden; }
.bar > div { height: 100%; background: var(--accent); width: 0; }
.meta { color: var(--muted); font-size: 12px; }
button, select, input[type=text] { font: inherit; color: inherit; background: var(--card);
  border: 1px solid var(--line); border-radius: 6px; padding: 6px 10px; }
button { cursor: pointer; }
button.primary { background: var(--accent); color: var(--accent-fg); border-color: var(--accent); }
.notice { margin: 12px 16px 0; padding: 8px 12px; border: 1px solid var(--line);
  border-radius: 8px; background: var(--card); font-size: 13px; }
.notice.round2 { border-color: var(--warn); }
main { display: grid; grid-template-columns: minmax(0, 1.6fr) minmax(300px, 1fr); gap: 16px;
  padding: 16px; max-width: 1500px; margin: 0 auto; }
@media (max-width: 900px) { main { grid-template-columns: 1fr; } .panel { position: static; } }
pre { white-space: pre-wrap; word-break: break-word; background: var(--card);
  border: 1px solid var(--line); border-radius: 8px; padding: 12px; margin: 0;
  font: 13px/1.45 ui-monospace, Consolas, monospace; max-height: calc(100vh - 150px); overflow: auto; }
.panel { background: var(--card); border: 1px solid var(--line); border-radius: 8px;
  padding: 12px; align-self: start; position: sticky; top: 72px; }
.row { border-top: 1px solid var(--line); padding: 10px 0; }
.row:first-of-type { border-top: 0; padding-top: 0; }
.row h3 { margin: 0 0 6px; font-size: 14px; }
label.choice { display: grid; grid-template-columns: auto 1fr; gap: 2px 8px; padding: 5px 6px;
  border-radius: 6px; cursor: pointer; }
label.choice.selected { background: var(--sel); }
label.choice .help { grid-column: 2; color: var(--muted); font-size: 12px; }
.key { display: inline-block; min-width: 1.4em; text-align: center; border: 1px solid var(--line);
  border-radius: 4px; font-size: 11px; margin-right: 4px; color: var(--muted); }
input[type=text], select { width: 100%; margin-top: 6px; }
.state-done { color: var(--ok); } .state-todo { color: var(--warn); }
nav { display: flex; flex-wrap: wrap; gap: 8px; margin-top: 12px; }
#status { font-size: 12px; color: var(--muted); }
</style>
</head>
<body>
<header>
  <h1 id="title"></h1>
  <div class="progress"><div class="bar"><div id="bar"></div></div><div class="meta" id="progress"></div></div>
  <button id="prev" title="Previous item (k or Left)">Previous</button>
  <button id="next" title="Next item (j or Right)">Next</button>
  <button id="nextTodo" title="Next unlabelled item (u)">Next unlabelled</button>
  <button id="download" class="primary">Download CSV</button>
  <span id="status"></span>
</header>
<div class="notice">Read only: nothing in a packet runs or loads. Labels save in this browser as you go.
When finished, or at the end of each session, click Download CSV and run
<code>python scripts/annotation_kit.py import &lt;downloaded file&gt;</code>. Definitions:
<code>docs/validation/ANNOTATION_GUIDELINE.md</code>. Keys: 1 to 5 choose, j and k move, u jumps to the next unlabelled item.</div>
<div class="notice round2" id="round2" hidden>Round 2: label without looking at your round 1 labels.
Only label an item at least 7 days after its round 1 label, and put today's date in the notes.</div>
<main>
  <section><div class="meta" id="itemMeta"></div><pre id="packet"></pre></section>
  <aside class="panel" id="panel"></aside>
</main>
<script>
const DATA = __DATA__;
const storeKey = "p01-labels:" + DATA.kind + ":" + DATA.rater + ":r" + DATA.round;
const $ = (id) => document.getElementById(id);
let idx = 0;

function rowKey(item, row) {
  return DATA.kind === "signals" ? item.key + "|" + row.rule_id : item.key;
}
function loadSaved() {
  let saved = {};
  try { saved = JSON.parse(localStorage.getItem(storeKey) || "{}"); } catch (e) { saved = {}; }
  for (const item of DATA.items) {
    for (const row of item.rows) {
      const s = saved[rowKey(item, row)];
      if (s) { row.label = s.label || ""; row.missed_category = s.missed_category || ""; row.notes = s.notes || ""; }
    }
  }
}
function persist() {
  const out = {};
  for (const item of DATA.items) {
    for (const row of item.rows) {
      if (row.label || row.notes || row.missed_category) {
        out[rowKey(item, row)] = { label: row.label || "", missed_category: row.missed_category || "", notes: row.notes || "" };
      }
    }
  }
  try { localStorage.setItem(storeKey, JSON.stringify(out)); $("status").textContent = "Saved in this browser"; }
  catch (e) { $("status").textContent = "Browser storage unavailable: download the CSV often"; }
}
function rowDone(row) {
  if (!row.label) return false;
  if (row.label === "MISSED_RISKY" && !row.missed_category) return false;
  return true;
}
function itemDone(item) { return item.rows.every(rowDone); }
function choicesFor(row) {
  if (DATA.kind === "signals") return row.rule_id === DATA.noneRule ? DATA.choices.none : DATA.choices.rule;
  return DATA.choices.pair;
}
function el(tag, text, cls) {
  const e = document.createElement(tag);
  if (text !== undefined) e.textContent = text;
  if (cls) e.className = cls;
  return e;
}
function updateProgress() {
  let rows = 0, done = 0, itemsDone = 0;
  for (const it of DATA.items) {
    for (const r of it.rows) { rows++; if (rowDone(r)) done++; }
    if (itemDone(it)) itemsDone++;
  }
  $("progress").textContent = done + " of " + rows + " label rows done; " + itemsDone + " of " + DATA.items.length + " items complete";
  $("bar").style.width = (rows ? (100 * done / rows) : 0) + "%";
}
function renderPanel() {
  const item = DATA.items[idx];
  const panel = $("panel");
  panel.replaceChildren();
  item.rows.forEach((row, rIndex) => {
    const box = el("div", undefined, "row");
    let heading;
    if (DATA.kind === "signals") heading = row.rule_id === DATA.noneRule ? "No rule matched: is a high-risk capability present?" : "Rule " + row.rule_id;
    else heading = DATA.kind === "lineage" ? "Same lineage?" : "What kind of change is this?";
    box.appendChild(el("h3", heading));
    choicesFor(row).forEach((choice, cIndex) => {
      const lab = el("label", undefined, "choice" + (row.label === choice ? " selected" : ""));
      const input = document.createElement("input");
      input.type = "radio";
      input.name = "row" + rIndex;
      input.checked = row.label === choice;
      input.addEventListener("change", () => { row.label = choice; if (choice !== "MISSED_RISKY") row.missed_category = ""; persist(); render(false); });
      const text = el("span");
      if (rIndex === firstOpenRow(item)) text.appendChild(el("span", String(cIndex + 1), "key"));
      text.appendChild(document.createTextNode(choice));
      lab.appendChild(input);
      lab.appendChild(text);
      lab.appendChild(el("span", DATA.help[choice] || "", "help"));
      box.appendChild(lab);
    });
    if (DATA.kind === "signals" && row.label === "MISSED_RISKY") {
      const sel = document.createElement("select");
      sel.appendChild(new Option("Choose the missed category", ""));
      for (const c of DATA.categories) sel.appendChild(new Option(c, c, false, row.missed_category === c));
      sel.addEventListener("change", () => { row.missed_category = sel.value; persist(); render(false); });
      box.appendChild(sel);
    }
    const notes = document.createElement("input");
    notes.type = "text";
    notes.placeholder = "Notes (optional; round 2: add today's date)";
    notes.value = row.notes || "";
    notes.addEventListener("input", () => { row.notes = notes.value; persist(); });
    box.appendChild(notes);
    panel.appendChild(box);
  });
  const state = el("div", itemDone(item) ? "Item complete" : "Item needs labels", itemDone(item) ? "state-done" : "state-todo");
  panel.appendChild(state);
}
function firstOpenRow(item) {
  const i = item.rows.findIndex((r) => !rowDone(r));
  return i === -1 ? 0 : i;
}
function render(scroll) {
  const item = DATA.items[idx];
  $("title").textContent = "P-01 labelling: " + DATA.kind + " (rater " + DATA.rater + ", round " + DATA.round + ")";
  $("itemMeta").textContent = "Item " + (idx + 1) + " of " + DATA.items.length + ": " + item.key.slice(0, 12) + (item.key.includes("|") ? " / " + item.key.split("|")[1].slice(0, 12) : "");
  $("packet").textContent = item.packet;
  if (scroll) $("packet").scrollTop = 0;
  renderPanel();
  updateProgress();
}
function go(delta) { idx = Math.min(DATA.items.length - 1, Math.max(0, idx + delta)); render(true); }
function nextTodo() {
  for (let step = 1; step <= DATA.items.length; step++) {
    const j = (idx + step) % DATA.items.length;
    if (!itemDone(DATA.items[j])) { idx = j; render(true); return; }
  }
  $("status").textContent = "Every item is labelled. Download the CSV.";
}
function csvCell(s) {
  s = String(s === undefined || s === null ? "" : s);
  return /[",\r\n]/.test(s) ? '"' + s.replace(/"/g, '""') + '"' : s;
}
function toCsv() {
  const lines = [DATA.columns.join(",")];
  for (const it of DATA.items) {
    for (const r of it.rows) {
      let rec;
      if (DATA.kind === "signals") {
        rec = { file_sha: it.key, rule_id: r.rule_id, label: r.label || "", missed_category: r.label === "MISSED_RISKY" ? (r.missed_category || "") : "", notes: r.notes || "" };
      } else {
        rec = { file_sha_a: r.file_sha_a, file_sha_b: r.file_sha_b, notes: r.notes || "" };
        rec[DATA.labelColumn] = r.label || "";
      }
      lines.push(DATA.columns.map((c) => csvCell(rec[c])).join(","));
    }
  }
  return lines.join("\r\n") + "\r\n";
}
function download() {
  const blob = new Blob([toCsv()], { type: "text/csv;charset=utf-8" });
  const a = document.createElement("a");
  a.href = URL.createObjectURL(blob);
  a.download = DATA.filename;
  document.body.appendChild(a);
  a.click();
  setTimeout(() => { URL.revokeObjectURL(a.href); a.remove(); }, 1000);
  $("status").textContent = "Downloaded " + DATA.filename;
}
document.addEventListener("keydown", (ev) => {
  const t = ev.target;
  if (t && (t.tagName === "INPUT" && t.type === "text" || t.tagName === "SELECT" || t.tagName === "TEXTAREA")) return;
  if (ev.key === "j" || ev.key === "ArrowRight") { go(1); ev.preventDefault(); }
  else if (ev.key === "k" || ev.key === "ArrowLeft") { go(-1); ev.preventDefault(); }
  else if (ev.key === "u") { nextTodo(); ev.preventDefault(); }
  else if (/^[1-9]$/.test(ev.key)) {
    const item = DATA.items[idx];
    const row = item.rows[firstOpenRow(item)];
    const choice = choicesFor(row)[Number(ev.key) - 1];
    if (choice) { row.label = choice; if (choice !== "MISSED_RISKY") row.missed_category = ""; persist(); render(false); }
  }
});
$("prev").addEventListener("click", () => go(-1));
$("next").addEventListener("click", () => go(1));
$("nextTodo").addEventListener("click", nextTodo);
$("download").addEventListener("click", download);
if (DATA.round >= 2) $("round2").hidden = false;
loadSaved();
if (DATA.items.length) { render(true); } else { $("packet").textContent = "No items for this kind and round."; }
</script>
</body>
</html>
"""
