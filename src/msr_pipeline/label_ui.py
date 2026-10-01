"""Labelling studio and CSV import for the P-01 validation kit.

`python scripts/annotation_kit.py ui --rater jd --round 1` writes one self-contained HTML
page per label kind into data/annotations/work/ (gitignored): the labelling studio. It shows
each reading packet as plain text with the matched text highlighted, explains the task with
text read from docs/validation/ANNOTATION_GUIDELINE.md when the page is built (so the studio
cannot drift from the guideline), keeps labels in the browser's local storage, and downloads
a CSV in the exact label-file format. `python scripts/annotation_kit.py import <csv>`
validates that download and writes it to data/annotations/.

The studio never chooses or pre-fills a label. Its step-through of the guideline's decision
order only applies the rater's own answers, and the rater still clicks to use the result.

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
from .config import repo_root

_SIGNAL_SHA = re.compile(r"^- file_sha: `([^`\s]+)`", re.M)
_PAIR_A = re.compile(r"^- file_sha_a: `([^`\s]+)`", re.M)
_PAIR_B = re.compile(r"^- file_sha_b: `([^`\s]+)`", re.M)
_LABEL_FILE = re.compile(r"^(signals|lineage|drift)_([a-z0-9][a-z0-9-]*)_r(\d+)\.csv$")
_DOWNLOAD_SUFFIX = re.compile(r"\s*\(\d+\)(?=\.csv$)")

GUIDELINE_PATH = repo_root() / "docs" / "validation" / "ANNOTATION_GUIDELINE.md"

# Fallback reminders, used only when the guideline file cannot be read. The studio otherwise
# shows the guideline's own definitions.
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

# Due dates and the round 2 gap, from docs/validation/README.md (D-022): signals and lineage
# rely on the primary rater's own round 2, so it waits at least 14 days; drift has a second
# rater, and its optional round 2 waits at least 7.
ROUND_DUE = {
    ("signals", 1): "2026-10-13",
    ("lineage", 1): "2026-10-13",
    ("drift", 1): "2026-10-16",
    ("signals", 2): "2026-10-27",
    ("lineage", 2): "2026-10-27",
    ("drift", 2): "2026-10-27",
}
ROUND2_MIN_DAYS = {"signals": 14, "lineage": 14, "drift": 7}

# What each kind's labels are for, in plain words.
KIND_BRIEF = {
    "signals": (
        "Each item is a skill that one or more rules flagged, or one of 40 skills no rule "
        "flagged. Your labels measure how often each rule is right (precision) and how much "
        "the rules miss (recall, from the no-signal skills). They decide whether the RQ1 "
        "prevalence numbers can be reported as risky capabilities or only as keyword matches. "
        "Hypothesis H1: at least one category reaches 80% precision."
    ),
    "lineage": (
        "Each item is a pair of skills the similarity method linked as versions of the same "
        "skill. Your labels measure how often that link is real (lineage precision), which "
        "every RQ3 drift pair depends on."
    ),
    "drift": (
        "Each item is a pair of versions whose high-risk categories differ. Your labels say "
        "what kind of change explains the difference. With two raters, Cohen's kappa shows "
        "whether these change types can be applied consistently, which decides how the "
        "report may describe RQ3."
    ),
}

# What the fields at the top of a reading packet mean. tests/test_label_ui.py checks that
# each field still appears in the packets annotation_kit.py writes.
FIELD_HELP = {
    "signals": [
        [
            "file_sha",
            "The skill text's fingerprint. It identifies the item in your label file; you never need to look it up.",
        ],
        ["front-matter name", "The name the skill gives itself at the top of its SKILL.md."],
        [
            "stratum",
            "Why this skill is in the sample: the risk category it was drawn for (about 10 per category), or NO_SIGNAL for the 40 skills no rule matched, which check for misses.",
        ],
        [
            "matched rules",
            'Every rule that matched. Sections marked "label this rule" (severity 6 or more) get a label row; "context only" rules do not.',
        ],
        ["Rule note", "The rule's own rationale and known false positives, from the rule file."],
    ],
    "pairs": [
        [
            "file_sha_a / file_sha_b",
            "The two versions' fingerprints. When ordered is True, a is the older version.",
        ],
        ["front-matter names", "The names the two versions give themselves."],
        [
            "similarity",
            "Word 5-chunk Jaccard similarity, 0 to 1. Context only: the guideline says it must not decide the label.",
        ],
        [
            "source",
            'Lineage only: why the pair was sampled. "differing" is one of the 18 pairs whose high-risk categories differ; "random" is one of 40 random pairs.',
        ],
        [
            "ordered",
            "True when both versions have first-commit dates, so a is older than b. False means the order is unknown.",
        ],
        [
            "only_in_a / only_in_b",
            "High-risk categories the detector found in only one version: what it thinks changed.",
        ],
        [
            "Unified diff, a to b",
            "Lines starting with - are only in a, lines starting with + only in b, other lines are shared.",
        ],
    ],
}

_HEADING = re.compile(r"^(#{2,3})\s+(\d+(?:\.\d+)?)\.?\s+(.*)$")
_VERSION = re.compile(r"^#\s+Annotation guideline \(version ([\d.]+), (\d{4}-\d{2}-\d{2})\)", re.M)
_CELL_SPLIT = re.compile(r"(?<!\\)\|")
_SEPARATOR = re.compile(r"^:?-{3,}:?$")
_BOLD = re.compile(r"\*\*(.+?)\*\*")
_NUMBERED = re.compile(r"^\d+\.\s+")
_CATEGORY = re.compile(r"\b[A-Z][A-Z_]{3,}\b")
_SIGNAL_OUTCOME = re.compile(r"\b(RISKY|BENIGN_CONTEXT|NOT_PRESENT)\b")


def _sections(text: str) -> dict[str, list[str]]:
    """Lines under each numbered heading (## 1., ### 2.1, ...), keyed by its number."""
    out: dict[str, list[str]] = {}
    current = None
    for line in text.splitlines():
        m = _HEADING.match(line)
        if m:
            current = m.group(2)
            out[current] = []
        elif current is not None:
            out[current].append(line)
    return out


def _table(lines: list[str]) -> list[list[str]]:
    """The first markdown table in ``lines``: header row first, separator dropped."""
    rows: list[list[str]] = []
    for line in lines:
        s = line.strip()
        if not s.startswith("|"):
            if rows:
                break
            continue
        cells = [c.strip().replace("\\|", "|") for c in _CELL_SPLIT.split(s)[1:-1]]
        if all(_SEPARATOR.match(c) for c in cells):
            continue
        rows.append(cells)
    return rows


def _paragraphs(lines: list[str]) -> list[str]:
    """Plain paragraphs (not tables, list items, or blank lines) in ``lines``."""
    out, buf = [], []
    for line in [*lines, ""]:
        s = line.strip()
        if not s or s.startswith("|") or s.startswith("- ") or _NUMBERED.match(s):
            if buf:
                out.append(" ".join(buf))
                buf = []
            continue
        buf.append(s)
    return out


def _question(lines: list[str]) -> str:
    for para in _paragraphs(lines):
        if "question" in para.lower():
            m = _BOLD.search(para)
            if m:
                return m.group(1)
    return ""


def parse_guideline(text: str) -> dict:
    """The parts of the annotation guideline the studio shows, read from its markdown.

    Raises ValueError if a part is missing, so a change to the guideline's structure is
    noticed when the page is built instead of producing a studio with gaps.
    """
    s = _sections(text)
    for number in ("1", "2", "2.1", "2.2", "2.3", "2.4", "2.5", "3", "4", "5", "7"):
        if number not in s:
            raise ValueError(f"guideline section {number} not found")
    m = _VERSION.search(text)

    decision = []
    for item in [_NUMBERED.sub("", x.strip()) for x in s["2.2"] if _NUMBERED.match(x.strip())]:
        bold = _BOLD.search(item)
        outcomes = _SIGNAL_OUTCOME.findall(item)
        decision.append(
            {
                "question": bold.group(1) if bold else "",
                "detail": item[bold.end() :].strip() if bold else item,
                "label": outcomes[-1] if outcomes else "",
            }
        )

    examples: dict[str, dict] = {}
    table = _table(s["2.3"])
    header = table[0] if table else []
    for row in table[1:]:
        cats = [c for c in _CATEGORY.findall(row[0]) if c not in v.SIGNAL_LABELS]
        for cat in cats:
            examples[cat] = {
                "capability": row[0],
                **{header[i]: row[i] for i in range(1, len(row))},
            }

    def label_table(rows: list[list[str]]) -> dict[str, dict]:
        head = [h.lower() for h in rows[0]] if rows else []
        return {r[0]: {head[i]: r[i] for i in range(1, len(r))} for r in rows[1:]}

    reason = next(
        (p for p in _paragraphs(s["5"]) if p.startswith("A reason states the evidence")), ""
    )
    times = {r[0]: r[1] for r in _table(s["7"])[1:]}
    guide = {
        "version": m.group(1) if m else "",
        "date": m.group(2) if m else "",
        "safety": [_NUMBERED.sub("", x.strip()) for x in s["1"] if _NUMBERED.match(x.strip())],
        "signals": {
            "question": _question(s["2"]),
            "labels": {r[0]: r[1] for r in _table(s["2.1"])[1:]},
            "decision": decision,
            "examples": examples,
            "special": [x.strip()[2:] for x in s["2.4"] if x.strip().startswith("- ")],
            "none": {r[0]: r[1] for r in _table(s["2.5"])[1:]},
            "noneNote": " ".join(_paragraphs(s["2.5"])),
        },
        "lineage": {
            "question": _question(s["3"]),
            "labels": label_table(_table(s["3"])),
            "note": " ".join(p for p in _paragraphs(s["3"]) if "question" not in p.lower()),
        },
        "drift": {
            "question": _question(s["4"]),
            "intro": " ".join(p for p in _paragraphs(s["4"]) if "question" in p.lower()),
            "labels": label_table(_table(s["4"])),
            "note": " ".join(p for p in _paragraphs(s["4"]) if "question" not in p.lower()),
        },
        "reason": reason,
        "times": times,
    }
    if len(decision) != 5 or not guide["signals"]["labels"] or not guide["safety"]:
        raise ValueError("guideline decision order, signal labels, or safety rules not found")
    return guide


def load_guideline(path: Path | None = None) -> dict | None:
    """The parsed guideline, or None when the file is not there (the page then falls back)."""
    path = path or GUIDELINE_PATH
    if not path.exists():
        return None
    return parse_guideline(path.read_text(encoding="utf-8"))


def _minutes(text: str) -> int:
    """The largest whole number in a time estimate such as "about 3 to 4 minutes"."""
    nums = [int(x) for x in re.findall(r"\d+", text or "")]
    return max(nums) if nums else 0


def _independence(kind: str, rater: str, round_: int) -> list[str]:
    """Who may see what, from docs/validation/README.md and the guideline's section 5."""
    out = []
    if round_ >= 2:
        out.append(
            f"Round 2: label without looking at your round 1 labels or file. Label an item only "
            f"if its round 1 label is at least {ROUND2_MIN_DAYS[kind]} days old, and put today's "
            "date in its notes."
        )
    if rater != "jd" and not rater.startswith("llm-"):
        out.append(
            "You are a second rater. Never open another rater's label files (for example any "
            "file ending _jd_r1.csv), and do not discuss specific items with them until both "
            "label files for this kind are merged. Your pull request contains only your own "
            "label file."
        )
    if rater == "jd" and kind == "drift" and round_ == 1:
        out.append(
            "Blindness rule: your filled drift file stays uncommitted until the second rater's "
            "drift labels (la) are merged."
        )
    if rater == "jd" and kind in ("signals", "lineage") and round_ == 1:
        out.append(
            "No teammate second-rates this kind (D-022). Its reliability comes from your own "
            "round 2 on a 30% subset at least 14 days from now, so keep no notes outside this "
            "page that you could look at then."
        )
    if rater.startswith("llm-"):
        out.append(
            "An llm- rater is reported as human-vs-LLM only, never as human agreement, and must "
            "be recorded in ai-use-log.md (guideline section 6)."
        )
    return out


def _next_steps(kind: str, rater: str) -> list[str]:
    steps = [
        "Label in sessions of 30 to 40 minutes. The page saves as you go, in this browser only.",
        "At the end of every session, click Download CSV.",
        "Save it into the project: drag the downloaded file onto windows/4-save-my-labels.bat, or "
        "run `python scripts/annotation_kit.py import <downloaded file>`. That checks every label "
        "and reason.",
        "When every item is done, open a pull request that contains only your label file "
        "(docs/NO_GIT_GUIDE.md, recipe 5), and ask a teammate to check that it imports cleanly.",
    ]
    if rater == "jd" and kind == "drift":
        steps[3] = (
            "When every item is done, keep the file uncommitted until the second rater's drift "
            "file is merged (blindness rule), then open your pull request."
        )
    return steps


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


def build_html(
    kind: str,
    rater: str,
    round_: int,
    items: list[dict],
    categories: list[str],
    rules: list[dict] | None = None,
    guide: dict | None = None,
    category_text: dict[str, str] | None = None,
) -> str:
    """Render the self-contained labelling studio.

    ``rules`` are rule-file entries (for the rule cards and highlighting); ``guide`` is the
    parsed guideline (read from GUIDELINE_PATH when not given). Labels already in ``items``
    are shown as they are; nothing is filled in for the rater.
    """
    if guide is None:
        guide = load_guideline()
    help_text = dict(LABEL_HELP)
    if guide:
        help_text.update(guide["signals"]["labels"])
        help_text.update(guide["signals"]["none"])
        for k in ("lineage", "drift"):
            help_text.update({lab: d.get("meaning", "") for lab, d in guide[k]["labels"].items()})
    times = (guide or {}).get("times", {})
    minutes = {
        "signals": _minutes(next((t for k, t in times.items() if k.startswith("Signal")), "3")),
        "none": _minutes(next((t for k, t in times.items() if k.startswith("No-signal")), "4")),
        "lineage": _minutes(next((t for k, t in times.items() if k.startswith("Lineage")), "2")),
        "drift": _minutes(next((t for k, t in times.items() if k.startswith("Drift")), "4")),
    }
    rule_cards = {}
    for r in rules or []:
        if str(r.get("status", "active")) != "active":
            continue
        examples = r.get("examples") or {}
        rule_cards[str(r["id"])] = {
            "category": str(r["category"]),
            "severity": int(r["severity"]),
            "note": str(r.get("note", "")),
            "patterns": [str(p) for p in r.get("patterns") or []],
            "flags": "gm" if r.get("case_sensitive") else "gim",
            "match": [str(x) for x in examples.get("match") or []],
            "noMatch": [str(x) for x in examples.get("no_match") or []],
        }
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
        "help": help_text,
        "justifyLabels": list(v.JUSTIFY_LABELS[kind]),
        "minNote": v.MIN_JUSTIFICATION_CHARS,
        "categories": list(categories),
        "categoryText": dict(category_text or {}),
        "items": items,
        "guide": guide,
        "rules": rule_cards,
        "brief": KIND_BRIEF[kind],
        "fields": FIELD_HELP["signals" if kind == "signals" else "pairs"],
        "independence": _independence(kind, rater, round_),
        "nextSteps": _next_steps(kind, rater),
        "due": ROUND_DUE.get((kind, round_), ""),
        "minutes": minutes,
        "round2Days": ROUND2_MIN_DAYS[kind],
    }
    # Escaping every "<" as a JSON unicode escape keeps packet text such as "</script>" or "<!--"
    # from interacting with the HTML parser; JSON and JavaScript both decode it back to "<".
    payload = json.dumps(data, ensure_ascii=False).replace("<", "\\u003c")
    title = html.escape(f"P-01 labelling studio: {kind}, rater {rater}, round {round_}")
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
:root { --bg:#f5f6f8; --fg:#15181e; --muted:#5f6573; --card:#ffffff; --line:#d9dde4; --soft:#eef1f5;
  --accent:#1c5cab; --accent-fg:#ffffff; --sel:#e4eefb; --ok:#1d7a2a; --warn:#8a6100; --bad:#b42318;
  --warn-soft:#fff4dc; --bad-soft:#fde8e6; --mark:#ffe08a; --mark-fg:#15181e; }
@media (prefers-color-scheme: dark) {
  :root { --bg:#111419; --fg:#eceff4; --muted:#9aa2b1; --card:#1a1e25; --line:#2c323d; --soft:#222731;
    --accent:#7fb2ef; --accent-fg:#0f1217; --sel:#1e2c42; --ok:#5fc46c; --warn:#e8c25f; --bad:#f08a80;
    --warn-soft:#33290d; --bad-soft:#3a1a17; --mark:#8a6d12; --mark-fg:#ffffff; }
}
* { box-sizing: border-box; }
[hidden] { display: none !important; }
body { margin: 0; background: var(--bg); color: var(--fg); font: 15px/1.5 system-ui, -apple-system, "Segoe UI", sans-serif; }
code { font: 0.88em ui-monospace, Consolas, monospace; background: var(--soft); padding: 0 4px; border-radius: 3px; }
header { position: sticky; top: 0; z-index: 3; background: var(--card); border-bottom: 1px solid var(--line);
  padding: 10px 16px; display: flex; flex-wrap: wrap; gap: 8px 12px; align-items: center; }
header h1 { font-size: 16px; margin: 0; }
.progress { flex: 1 1 220px; min-width: 180px; }
.bar { height: 6px; background: var(--line); border-radius: 3px; overflow: hidden; }
.bar > div { height: 100%; background: var(--accent); width: 0; }
.meta { color: var(--muted); font-size: 12px; }
button, select, input[type=text], textarea { font: inherit; color: inherit; background: var(--card);
  border: 1px solid var(--line); border-radius: 6px; padding: 6px 10px; }
button { cursor: pointer; }
button:focus-visible, select:focus-visible, textarea:focus-visible, summary:focus-visible { outline: 2px solid var(--accent); outline-offset: 2px; }
button.primary { background: var(--accent); color: var(--accent-fg); border-color: var(--accent); }
button.small { padding: 3px 10px; font-size: 13px; }
button:disabled { opacity: 0.5; cursor: not-allowed; }
.banner { margin: 10px 16px 0; padding: 8px 12px; border-radius: 8px; font-size: 13px; display: flex; flex-wrap: wrap; gap: 8px; align-items: center; }
.banner.warn { background: var(--warn-soft); }
.banner.info { background: var(--sel); }
main { display: grid; grid-template-columns: minmax(0, 1.55fr) minmax(320px, 1fr); gap: 16px; padding: 16px; max-width: 1500px; margin: 0 auto; }
@media (max-width: 900px) { main { grid-template-columns: 1fr; } .panel { position: static !important; max-height: none !important; } }
.left { display: grid; gap: 10px; align-content: start; min-width: 0; }
pre { white-space: pre-wrap; word-break: break-word; background: var(--card); border: 1px solid var(--line); border-radius: 8px;
  padding: 12px; margin: 0; font: 13px/1.5 ui-monospace, Consolas, monospace; max-height: calc(100vh - 210px); overflow: auto; }
mark { background: var(--mark); color: var(--mark-fg); border-radius: 2px; padding: 0 1px; }
.panel { background: var(--card); border: 1px solid var(--line); border-radius: 8px; padding: 12px; align-self: start;
  position: sticky; top: 70px; max-height: calc(100vh - 86px); overflow: auto; display: grid; gap: 10px; }
.row { border-top: 1px solid var(--line); padding-top: 10px; display: grid; gap: 8px; }
.row:first-child { border-top: 0; padding-top: 0; }
.row h3 { margin: 0; font-size: 14px; }
details.card { border: 1px solid var(--line); border-radius: 6px; padding: 6px 10px; background: var(--card); }
details.card > summary { cursor: pointer; font-size: 13px; font-weight: 600; }
details.card[open] > summary { margin-bottom: 6px; }
details.card p, details.card li { font-size: 13px; margin: 4px 0; }
details.card ul { padding-left: 1.2em; margin: 4px 0; }
.ex { display: grid; grid-template-columns: max-content 1fr; gap: 4px 10px; font-size: 13px; }
.ex b { font-size: 12px; }
.wizard { border-left: 3px solid var(--accent); padding: 4px 0 4px 10px; display: grid; gap: 6px; font-size: 13px; }
.wizard .q { font-weight: 600; font-size: 14px; }
.wizard .detail { color: var(--muted); margin: 0; }
.wizard .answered { color: var(--muted); }
.wizard .n { font-family: ui-monospace, Consolas, monospace; color: var(--muted); }
.wizard .outcome { display: flex; flex-wrap: wrap; gap: 6px; align-items: center; background: var(--sel); border-radius: 6px; padding: 6px 8px; }
.btns { display: flex; gap: 6px; flex-wrap: wrap; }
label.choice { display: grid; grid-template-columns: auto 1fr; gap: 2px 8px; padding: 6px; border-radius: 6px; cursor: pointer; border: 1px solid transparent; }
label.choice:hover { border-color: var(--line); }
label.choice.selected { background: var(--sel); border-color: var(--accent); }
label.choice .help { grid-column: 2; color: var(--muted); font-size: 12px; }
label.choice .help.example { font-style: italic; }
.key { display: inline-block; min-width: 1.4em; text-align: center; border: 1px solid var(--line); border-radius: 4px; font-size: 11px; margin-right: 4px; color: var(--muted); }
textarea { width: 100%; min-height: 64px; resize: vertical; }
textarea.needs-reason { border: 2px solid var(--bad); background: var(--bad-soft); }
.problems { margin: 0; padding-left: 1.2em; font-size: 12px; color: var(--bad); }
.chips { display: flex; gap: 6px; flex-wrap: wrap; }
.escalated { background: var(--bad-soft); border-radius: 6px; padding: 8px 10px; font-size: 13px; }
.state-done { color: var(--ok); font-weight: 600; } .state-todo { color: var(--warn); font-weight: 600; }
.gate { background: var(--sel); border-radius: 6px; padding: 10px; display: grid; gap: 8px; font-size: 14px; }
#status { font-size: 12px; color: var(--muted); }
dl.fields { display: grid; grid-template-columns: max-content 1fr; gap: 4px 12px; font-size: 13px; margin: 0; }
dl.fields dt { font-family: ui-monospace, Consolas, monospace; font-size: 12px; }
dl.fields dd { margin: 0; color: var(--muted); }
.overlay { position: fixed; inset: 0; z-index: 10; background: rgba(10, 12, 16, 0.55); display: flex; justify-content: center; align-items: flex-start; overflow: auto; padding: 24px 12px; }
.overlay[hidden] { display: none; }
.sheet { background: var(--card); color: var(--fg); border-radius: 10px; max-width: 860px; width: 100%; padding: 20px 22px; display: grid; gap: 14px; }
.sheet h2 { margin: 0; font-size: 20px; }
.sheet h3 { margin: 6px 0 0; font-size: 15px; }
.sheet p, .sheet li { max-width: 75ch; }
.sheet ol, .sheet ul { margin: 0; padding-left: 1.3em; display: grid; gap: 4px; }
.quote { border-left: 3px solid var(--accent); padding: 4px 0 4px 12px; font-weight: 600; }
table { border-collapse: collapse; width: 100%; font-size: 13px; }
th, td { text-align: left; padding: 5px 8px 5px 0; border-bottom: 1px solid var(--line); vertical-align: top; }
th { color: var(--muted); font-weight: 600; font-size: 12px; }
tr.jump { cursor: pointer; } tr.jump:hover { background: var(--soft); }
.tbl { overflow-x: auto; }
.facts { display: flex; flex-wrap: wrap; gap: 6px 18px; font-size: 14px; }
.facts b { font-variant-numeric: tabular-nums; }
</style>
</head>
<body>
<header>
  <h1 id="title"></h1>
  <div class="progress"><div class="bar"><div id="bar"></div></div><div class="meta" id="progress"></div></div>
  <button id="guideBtn" title="The briefing: task, rules, how to decide (?)">Guide</button>
  <button id="summaryBtn" title="Every item and its labels">Summary</button>
  <button id="prev" title="Previous item (k or Left)">Previous</button>
  <button id="next" title="Next item (j or Right)">Next</button>
  <button id="nextTodo" title="Next unfinished item (u)">Next unfinished</button>
  <button id="download" class="primary">Download CSV</button>
  <span id="status"></span>
</header>
<div class="banner info" id="round2" hidden></div>
<div class="banner warn" id="breakBanner" hidden><span id="breakText"></span><button id="breakDone" class="small">I took a break</button></div>
<main>
  <section class="left">
    <div class="meta" id="itemMeta"></div>
    <details class="card" id="fields"><summary>What the lines at the top of the text mean</summary><dl class="fields" id="fieldList"></dl></details>
    <pre id="packet"></pre>
    <div class="meta">Read only: nothing in this text runs or loads. Highlighted text is what the rules matched.</div>
  </section>
  <aside class="panel" id="panel"></aside>
</main>
<div class="overlay" id="guide" role="dialog" aria-modal="true" aria-labelledby="guideTitle" hidden><div class="sheet" id="guideSheet"></div></div>
<div class="overlay" id="summary" role="dialog" aria-modal="true" aria-labelledby="summaryTitle" hidden><div class="sheet" id="summarySheet"></div></div>
<script>
const DATA = __DATA__;
const storeKey = "p01-labels:" + DATA.kind + ":" + DATA.rater + ":r" + DATA.round;
const G = DATA.guide;
const briefKey = storeKey + ":briefed";
const $ = (id) => document.getElementById(id);
let idx = 0;
const wizard = {};
const sessionStart = Date.now();
let breakFrom = sessionStart;
const GENERIC = /^(false positive|fp|not risky|risky|benign|benign context|safe|fine|ok|okay|n\/?a|none|not present|yes|no|unsure|same|different)\.?$/i;
const LINKISH = /(https?:\/\/|www\.|github\.com|gitlab\.com)/i;
const SKIP_LINE = /^(# |## |> |- file_sha|- front-matter|- stratum|- matched rules|- similarity|- source|- ordered|- only_in_|Rule note:)/;

function el(tag, text, cls) {
  const e = document.createElement(tag);
  if (text !== undefined) e.textContent = text;
  if (cls) e.className = cls;
  return e;
}
function inline(text) {
  const frag = document.createDocumentFragment();
  for (const p of String(text || "").split(/(`[^`]+`|\*\*[^*]+\*\*)/)) {
    if (!p) continue;
    if (p.length > 1 && p.startsWith("`") && p.endsWith("`")) frag.appendChild(el("code", p.slice(1, -1)));
    else if (p.length > 3 && p.startsWith("**") && p.endsWith("**")) frag.appendChild(el("b", p.slice(2, -2)));
    else frag.appendChild(document.createTextNode(p));
  }
  return frag;
}
function para(text, cls, tag) { const p = el(tag || "p", undefined, cls); p.appendChild(inline(text)); return p; }
function list(items, ordered) { const l = el(ordered ? "ol" : "ul"); for (const t of items) l.appendChild(para(t, undefined, "li")); return l; }
function isBriefed() { try { return localStorage.getItem(briefKey) === "yes"; } catch (e) { return briefedThisPage; } }
let briefedThisPage = false;
function setBriefed() { briefedThisPage = true; try { localStorage.setItem(briefKey, "yes"); } catch (e) { /* page memory only */ } }

function rowKey(item, row) { return DATA.kind === "signals" ? item.key + "|" + row.rule_id : item.key; }
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
function needsReason(row) { return DATA.justifyLabels.indexOf(row.label) !== -1; }
function hasReason(row) { return (row.notes || "").trim().length >= DATA.minNote; }
function rowDone(row) {
  if (!row.label) return false;
  if (row.label === "MISSED_RISKY" && !row.missed_category) return false;
  if (needsReason(row) && !hasReason(row)) return false;
  return true;
}
function itemDone(item) { return item.rows.every(rowDone); }
function isNoneRow(row) { return DATA.kind === "signals" && row.rule_id === DATA.noneRule; }
function choicesFor(row) {
  if (DATA.kind === "signals") return isNoneRow(row) ? DATA.choices.none : DATA.choices.rule;
  return DATA.choices.pair;
}
function noteProblems(row) {
  const t = (row.notes || "").trim();
  const out = [];
  if (needsReason(row) && t.length < DATA.minNote) out.push("Required for " + row.label + ": at least " + DATA.minNote + " characters saying what the text actually shows.");
  if (t && GENERIC.test(t)) out.push("That is a conclusion. State the evidence: what the text actually was, and why the label fits.");
  if (LINKISH.test(t)) out.push("No links, repository names, or account names in notes (safety rule 2).");
  return out;
}
function field(packet, name) {
  const m = packet.match(new RegExp("^- " + name + ": (.*)$", "m"));
  return m ? m[1].replace(/`/g, "") : "";
}
function itemMinutes(item) {
  if (DATA.kind !== "signals") return DATA.minutes[DATA.kind] || 3;
  return item.rows.some(isNoneRow) ? DATA.minutes.none : DATA.minutes.signals;
}

// ---- packet with the matched text highlighted ------------------------------------------
function regexesFor(ids) {
  const out = [];
  for (const id of ids) {
    const r = DATA.rules[id];
    if (!r) continue;
    for (const p of r.patterns) { try { out.push(new RegExp(p, r.flags)); } catch (e) { /* pattern the browser cannot read */ } }
  }
  return out;
}
function highlighted(text, ids) {
  const res = regexesFor(ids);
  const frag = document.createDocumentFragment();
  if (!res.length) { frag.appendChild(document.createTextNode(text)); return { frag: frag, count: 0 }; }
  const ranges = [];
  let offset = 0;
  for (const line of text.split("\n")) {
    if (!SKIP_LINE.test(line)) {
      for (const re of res) {
        re.lastIndex = 0;
        let m, guard = 0;
        while ((m = re.exec(line)) && guard++ < 200) {
          if (!m[0].length) { re.lastIndex++; continue; }
          ranges.push([offset + m.index, offset + m.index + m[0].length]);
        }
      }
    }
    offset += line.length + 1;
  }
  ranges.sort((a, b) => a[0] - b[0]);
  const merged = [];
  for (const r of ranges) {
    const last = merged[merged.length - 1];
    if (last && r[0] <= last[1]) last[1] = Math.max(last[1], r[1]); else merged.push([r[0], r[1]]);
  }
  let pos = 0;
  for (const [a, b] of merged) {
    if (a > pos) frag.appendChild(document.createTextNode(text.slice(pos, a)));
    frag.appendChild(el("mark", text.slice(a, b)));
    pos = b;
  }
  if (pos < text.length) frag.appendChild(document.createTextNode(text.slice(pos)));
  return { frag: frag, count: merged.length };
}

// ---- help in the panel ----------------------------------------------------------------
function ruleCard(ruleId) {
  const r = DATA.rules[ruleId];
  const d = el("details", undefined, "card");
  d.appendChild(el("summary", "About rule " + ruleId + (r ? " (" + r.category + ", severity " + r.severity + ")" : "")));
  if (!r) { d.appendChild(el("p", "This rule is not in the rule file the page was built with.")); return d; }
  if (DATA.categoryText[r.category]) d.appendChild(para(r.category + ": " + DATA.categoryText[r.category]));
  if (r.note) d.appendChild(para("Rule note: " + r.note));
  if (r.match.length) { d.appendChild(el("p", "The rule is written to match, for example:")); d.appendChild(list(r.match.map((x) => "`" + x + "`"))); }
  if (r.noMatch.length) { d.appendChild(el("p", "and not to match:")); d.appendChild(list(r.noMatch.map((x) => "`" + x + "`"))); }
  const ex = G && G.signals.examples[r.category];
  if (ex) {
    d.appendChild(el("p", "Guideline examples for " + ex.capability + " (all invented):"));
    const grid = el("div", undefined, "ex");
    for (const lab of DATA.choices.rule) { if (ex[lab]) { grid.appendChild(el("b", lab)); grid.appendChild(para(ex[lab], undefined, "span")); } }
    d.appendChild(grid);
  }
  return d;
}
function decisionHelper(item, row) {
  const steps = G.signals.decision;
  const key = rowKey(item, row);
  const st = wizard[key] || (wizard[key] = { step: 0, answers: [], outcome: "" });
  const box = el("div", undefined, "wizard");
  box.appendChild(el("div", "Guideline 2.2: answer the questions in order for this rule's match. The first one that settles it gives the label.", "meta"));
  st.answers.forEach((a, i) => {
    const line = el("div", undefined, "answered");
    line.appendChild(el("span", (i + 1) + ". ", "n"));
    line.appendChild(inline(steps[i].question));
    line.appendChild(el("b", "  " + a));
    box.appendChild(line);
  });
  if (st.outcome) {
    const res = el("div", undefined, "outcome");
    res.appendChild(document.createTextNode("Your answers give "));
    res.appendChild(el("b", st.outcome));
    const use = el("button", "Use " + st.outcome, "primary small");
    use.addEventListener("click", () => setLabel(row, st.outcome));
    const again = el("button", "Start over", "small");
    again.addEventListener("click", () => { delete wizard[key]; render(false); });
    res.appendChild(use);
    res.appendChild(again);
    box.appendChild(res);
    return box;
  }
  const s = steps[st.step];
  const q = el("div", undefined, "q");
  q.appendChild(el("span", (st.step + 1) + ". ", "n"));
  q.appendChild(inline(s.question));
  box.appendChild(q);
  if (s.detail) box.appendChild(para(s.detail, "detail"));
  const btns = el("div", undefined, "btns");
  if (st.step === steps.length - 1) {
    const b = el("button", "That leaves " + s.label, "small");
    b.addEventListener("click", () => { st.answers.push("(none of the above)"); st.outcome = s.label; render(false); });
    btns.appendChild(b);
  } else {
    // Steps whose label is NOT_PRESENT are settled by a "no" (it is not the capability, or not
    // an instruction); the others are settled by a "yes" (warned against, or gated).
    const settleOnNo = s.label === "NOT_PRESENT";
    const yes = el("button", "Yes", "small");
    const no = el("button", "No", "small");
    yes.addEventListener("click", () => { st.answers.push("Yes"); if (settleOnNo) st.step++; else st.outcome = s.label; render(false); });
    no.addEventListener("click", () => { st.answers.push("No"); if (settleOnNo) st.outcome = s.label; else st.step++; render(false); });
    btns.appendChild(yes);
    btns.appendChild(no);
  }
  box.appendChild(btns);
  return box;
}
function setLabel(row, choice) {
  row.label = choice;
  if (choice !== "MISSED_RISKY") row.missed_category = "";
  persist();
  render(false);
}
function choiceList(item, row, rIndex) {
  const box = el("div");
  const examples = G && DATA.kind !== "signals" ? G[DATA.kind].labels : null;
  choicesFor(row).forEach((choice, cIndex) => {
    const lab = el("label", undefined, "choice" + (row.label === choice ? " selected" : ""));
    const input = document.createElement("input");
    input.type = "radio";
    input.name = "row" + rIndex;
    input.checked = row.label === choice;
    input.addEventListener("change", () => setLabel(row, choice));
    const text = el("span");
    if (rIndex === firstOpenRow(item)) text.appendChild(el("span", String(cIndex + 1), "key"));
    text.appendChild(el("b", choice));
    lab.appendChild(input);
    lab.appendChild(text);
    lab.appendChild(para(DATA.help[choice] || "", "help", "span"));
    if (examples && examples[choice] && examples[choice].example) lab.appendChild(para("Example: " + examples[choice].example, "help example", "span"));
    box.appendChild(lab);
  });
  return box;
}
function notesBox(item, row) {
  const wrap = el("div");
  const notes = document.createElement("textarea");
  const must = needsReason(row);
  notes.placeholder = must
    ? "Why this label? Required: what the matched text actually was and why. Quote a few words at most; no repository names."
    : "Notes (optional)" + (DATA.round >= 2 ? "; round 2: add today's date" : "");
  notes.value = row.notes || "";
  notes.setAttribute("aria-label", "Notes for this row");
  const probs = el("ul", undefined, "problems");
  const refresh = () => {
    notes.className = must && !hasReason(row) ? "needs-reason" : "";
    probs.replaceChildren();
    for (const p of noteProblems(row)) probs.appendChild(el("li", p));
    const state = $("itemState");
    if (state) { const done = itemDone(item); state.textContent = done ? "Item complete" : "Item needs labels"; state.className = done ? "state-done" : "state-todo"; }
    updateProgress();
  };
  notes.addEventListener("input", () => { row.notes = notes.value; refresh(); persist(); });
  wrap.appendChild(notes);
  wrap.appendChild(probs);
  const chips = el("div", undefined, "chips");
  const add = (text) => { if (!(row.notes || "").toLowerCase().includes(text)) { row.notes = ((row.notes || "").trim() ? row.notes.trim() + "; " : "") + text; persist(); render(false); } };
  const t = el("button", "Mark truncated", "small");
  t.title = "The decisive context is cut off: label from what is shown (guideline 2.4).";
  t.addEventListener("click", () => add("truncated"));
  const e = el("button", "Escalate", "small");
  e.title = "Looks actively malicious (guideline 1.3).";
  e.addEventListener("click", () => add("escalate"));
  chips.appendChild(t);
  chips.appendChild(e);
  wrap.appendChild(chips);
  if (/\bescalate\b/i.test(row.notes || "")) {
    wrap.appendChild(el("div", "You marked this item for escalation. Label it, then stop and raise it with the instructor before going on (safety rule 3). Do not open, run, or search for anything from it.", "escalated"));
  }
  refresh();
  return wrap;
}
function renderPanel() {
  const item = DATA.items[idx];
  const panel = $("panel");
  panel.replaceChildren();
  if (!isBriefed()) {
    const gate = el("div", undefined, "gate");
    gate.appendChild(el("b", "Read the briefing before your first label."));
    gate.appendChild(el("span", "It explains the task, the safety rules, and how to decide. It takes about five minutes."));
    const b = el("button", "Open the briefing", "primary");
    b.addEventListener("click", openGuide);
    gate.appendChild(b);
    panel.appendChild(gate);
    return;
  }
  item.rows.forEach((row, rIndex) => {
    const box = el("div", undefined, "row");
    let heading;
    if (DATA.kind === "signals") heading = isNoneRow(row) ? "No rule matched. Is a high-risk capability present anyway?" : "Rule " + row.rule_id + ": is this capability really there?";
    else heading = DATA.kind === "lineage" ? "Same original skill?" : "What kind of change explains the difference?";
    box.appendChild(el("h3", heading));
    if (DATA.kind === "signals" && !isNoneRow(row)) {
      box.appendChild(ruleCard(row.rule_id));
      if (G) {
        const help = el("details", undefined, "card");
        help.open = !row.label;
        help.appendChild(el("summary", "Help me decide (the guideline's decision order)"));
        help.appendChild(decisionHelper(item, row));
        box.appendChild(help);
      }
    }
    if (isNoneRow(row) && G && G.signals.noneNote) box.appendChild(para(G.signals.noneNote, "meta"));
    if (DATA.kind === "lineage" && G && G.lineage.note) box.appendChild(para(G.lineage.note, "meta"));
    if (DATA.kind === "drift" && G && G.drift.intro) box.appendChild(para(G.drift.intro, "meta"));
    box.appendChild(choiceList(item, row, rIndex));
    if (DATA.kind === "drift" && G && G.drift.note) box.appendChild(para(G.drift.note, "meta"));
    if (isNoneRow(row) && row.label === "MISSED_RISKY") {
      const sel = document.createElement("select");
      sel.setAttribute("aria-label", "Missed category");
      sel.appendChild(new Option("Choose the missed category", ""));
      for (const c of DATA.categories) sel.appendChild(new Option(c + (DATA.categoryText[c] ? ": " + DATA.categoryText[c] : ""), c, false, row.missed_category === c));
      sel.addEventListener("change", () => { row.missed_category = sel.value; persist(); render(false); });
      box.appendChild(sel);
    }
    box.appendChild(notesBox(item, row));
    panel.appendChild(box);
  });
  const state = el("div", itemDone(item) ? "Item complete" : "Item needs labels", itemDone(item) ? "state-done" : "state-todo");
  state.id = "itemState";
  panel.appendChild(state);
}
function firstOpenRow(item) { const i = item.rows.findIndex((r) => !rowDone(r)); return i === -1 ? 0 : i; }
function updateProgress() {
  let rows = 0, done = 0, itemsDone = 0, minutesLeft = 0;
  for (const it of DATA.items) {
    for (const r of it.rows) { rows++; if (rowDone(r)) done++; }
    if (itemDone(it)) itemsDone++; else minutesLeft += itemMinutes(it);
  }
  const hours = minutesLeft >= 60 ? Math.floor(minutesLeft / 60) + " h " + (minutesLeft % 60) + " min" : minutesLeft + " min";
  $("progress").textContent = itemsDone + " of " + DATA.items.length + " items complete (" + done + " of " + rows + " label rows); about " + hours + " left" + (DATA.due ? "; due " + DATA.due : "");
  $("bar").style.width = (rows ? (100 * done / rows) : 0) + "%";
}
function render(scroll) {
  const item = DATA.items[idx];
  $("title").textContent = "Labelling studio: " + DATA.kind + ", rater " + DATA.rater + ", round " + DATA.round;
  let meta = "Item " + (idx + 1) + " of " + DATA.items.length;
  if (DATA.kind === "signals") {
    const s = field(item.packet, "stratum");
    if (s) meta += " · drawn for " + (s === "NO_SIGNAL" ? "no signal (checks for misses)" : s);
  } else {
    const sim = field(item.packet, "similarity"), ord = field(item.packet, "ordered"), src = field(item.packet, "source");
    if (sim) meta += " · similarity " + sim;
    if (ord) meta += " · ordered " + ord;
    if (src) meta += " · " + src;
  }
  const ids = DATA.kind === "signals" ? item.rows.map((r) => r.rule_id).filter((x) => x !== DATA.noneRule) : [];
  const h = highlighted(item.packet, ids);
  if (h.count) meta += " · " + h.count + " match" + (h.count > 1 ? "es" : "") + " highlighted";
  $("itemMeta").textContent = meta;
  $("packet").replaceChildren(h.frag);
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

// ---- briefing and summary ------------------------------------------------------------------
function section(sheet, title) { sheet.appendChild(el("h3", title)); }
function openGuide() {
  const sheet = $("guideSheet");
  sheet.replaceChildren();
  const h = el("h2", "Your job: " + DATA.kind + " labels, round " + DATA.round);
  h.id = "guideTitle";
  sheet.appendChild(h);
  const q = G && G[DATA.kind] && G[DATA.kind].question;
  if (q) sheet.appendChild(para(q, "quote"));
  sheet.appendChild(para(DATA.brief));
  let rows = 0, minutes = 0;
  for (const it of DATA.items) { rows += it.rows.length; minutes += itemMinutes(it); }
  const facts = el("div", undefined, "facts");
  const fact = (k, val) => { const s = el("span", k + ": "); s.appendChild(el("b", val)); facts.appendChild(s); };
  fact("Items", String(DATA.items.length));
  fact("Label rows", String(rows));
  fact("Time", "about " + Math.round(minutes / 60 * 10) / 10 + " hours, in 30 to 40 minute sessions");
  if (DATA.due) fact("Due", DATA.due);
  sheet.appendChild(facts);
  section(sheet, "Why a person has to do this");
  sheet.appendChild(para("The rules find words, not intentions. A skill can show a dangerous command to warn against it, or a rule can match a harmless string. Only a careful reader can tell, and your labels are what make the project's numbers trustworthy. Nothing in this page suggests a label: every label is your judgement, made from the guideline."));
  if (G) {
    section(sheet, "Safety rules (guideline 1)");
    sheet.appendChild(list(G.safety, true));
  }
  if (DATA.independence.length) { section(sheet, "Working independently"); sheet.appendChild(list(DATA.independence)); }
  section(sheet, "How to decide");
  if (!G) sheet.appendChild(el("p", "The guideline file was not found when this page was built, so only short definitions are shown. Read docs/validation/ANNOTATION_GUIDELINE.md."));
  else if (DATA.kind === "signals") {
    sheet.appendChild(para("For each rule row: " + G.signals.question));
    sheet.appendChild(list(G.signals.decision.map((s) => "**" + s.question + "** " + s.detail), true));
    const t = el("table");
    t.appendChild(el("tr")).append(el("th", "Label"), el("th", "Meaning"));
    for (const [lab, def] of Object.entries(G.signals.labels).concat(Object.entries(G.signals.none))) {
      const tr = el("tr"); tr.appendChild(el("td")).appendChild(el("b", lab)); tr.appendChild(el("td")).appendChild(inline(def)); t.appendChild(tr);
    }
    const tw = el("div", undefined, "tbl"); tw.appendChild(t); sheet.appendChild(tw);
    if (G.signals.noneNote) sheet.appendChild(para(G.signals.noneNote));
    sheet.appendChild(el("p", "Special cases (guideline 2.4):"));
    sheet.appendChild(list(G.signals.special));
  } else {
    const k = G[DATA.kind];
    if (k.intro) sheet.appendChild(para(k.intro));
    const t = el("table");
    t.appendChild(el("tr")).append(el("th", "Label"), el("th", "Meaning"), el("th", "Example"));
    for (const [lab, d] of Object.entries(k.labels)) {
      const tr = el("tr");
      tr.appendChild(el("td")).appendChild(el("b", lab));
      tr.appendChild(el("td")).appendChild(inline(d.meaning || ""));
      tr.appendChild(el("td")).appendChild(inline(d.example || ""));
      t.appendChild(tr);
    }
    const tw = el("div", undefined, "tbl"); tw.appendChild(t); sheet.appendChild(tw);
    if (k.note) sheet.appendChild(para(k.note));
  }
  section(sheet, "Reasons");
  sheet.appendChild(para("These labels need a written reason of at least " + DATA.minNote + " characters: " + DATA.justifyLabels.join(", ") + ". " + (G ? G.reason : "")));
  section(sheet, "When you finish a session");
  sheet.appendChild(list(DATA.nextSteps, true));
  if (G) sheet.appendChild(el("p", "Text on this page comes from ANNOTATION_GUIDELINE.md version " + G.version + " (" + G.date + ") and the rule file, read when the page was built.", "meta"));
  const ack = el("label");
  const box = document.createElement("input");
  box.type = "checkbox";
  box.checked = isBriefed();
  ack.appendChild(box);
  ack.appendChild(document.createTextNode(" I have read the safety rules and how to decide."));
  sheet.appendChild(ack);
  const btns = el("div", undefined, "btns");
  const start = el("button", isBriefed() ? "Back to labelling" : "Start labelling", "primary");
  start.disabled = !box.checked;
  box.addEventListener("change", () => { start.disabled = !box.checked; });
  start.addEventListener("click", () => { setBriefed(); closeOverlays(); render(false); });
  btns.appendChild(start);
  sheet.appendChild(btns);
  $("guide").hidden = false;
  start.focus();
}
function openSummary() {
  const sheet = $("summarySheet");
  sheet.replaceChildren();
  const h = el("h2", "Summary: " + DATA.kind + ", rater " + DATA.rater + ", round " + DATA.round);
  h.id = "summaryTitle";
  sheet.appendChild(h);
  const counts = {};
  let needReason = 0, escalated = 0, truncated = 0;
  for (const it of DATA.items) for (const r of it.rows) {
    counts[r.label || "not labelled"] = (counts[r.label || "not labelled"] || 0) + 1;
    if (r.label && needsReason(r) && !hasReason(r)) needReason++;
    if (/\bescalate\b/i.test(r.notes || "")) escalated++;
    if (/\btruncated\b/i.test(r.notes || "")) truncated++;
  }
  const facts = el("div", undefined, "facts");
  for (const [k, n] of Object.entries(counts)) { const s = el("span", k + ": "); s.appendChild(el("b", String(n))); facts.appendChild(s); }
  sheet.appendChild(facts);
  if (needReason) sheet.appendChild(el("p", needReason + " label rows still need a reason; the CSV will not import until they have one.", "problems"));
  if (escalated) sheet.appendChild(el("p", escalated + " marked escalate: raise them with the instructor.", "problems"));
  if (truncated) sheet.appendChild(el("p", truncated + " marked truncated.", "meta"));
  const t = el("table");
  t.appendChild(el("tr")).append(el("th", "#"), el("th", "Item"), el("th", "Labels"), el("th", "Status"));
  DATA.items.forEach((it, i) => {
    const tr = el("tr", undefined, "jump");
    tr.appendChild(el("td", String(i + 1)));
    tr.appendChild(el("td", it.key.split("|").map((x) => x.slice(0, 10)).join(" / ")));
    tr.appendChild(el("td", it.rows.map((r) => (DATA.kind === "signals" ? r.rule_id + ": " : "") + (r.label || "—")).join("; ")));
    tr.appendChild(el("td", itemDone(it) ? "done" : "open", itemDone(it) ? "state-done" : "state-todo"));
    tr.addEventListener("click", () => { idx = i; closeOverlays(); render(true); });
    t.appendChild(tr);
  });
  const tw = el("div", undefined, "tbl"); tw.appendChild(t); sheet.appendChild(tw);
  const close = el("button", "Close", "primary");
  close.addEventListener("click", closeOverlays);
  sheet.appendChild(close);
  $("summary").hidden = false;
  close.focus();
}
function closeOverlays() { $("guide").hidden = true; $("summary").hidden = true; }
function overlayOpen() { return !$("guide").hidden || !$("summary").hidden; }

// ---- CSV ---------------------------------------------------------------------------------
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
  $("status").textContent = "Downloaded " + DATA.filename + ". Next: save it into the project (Guide, last section).";
}

// ---- keys, timer, start ----------------------------------------------------------------------
document.addEventListener("keydown", (ev) => {
  if (ev.key === "Escape" && overlayOpen() && isBriefed()) { closeOverlays(); render(false); return; }
  if (overlayOpen()) return;
  const t = ev.target;
  if (t && (t.tagName === "INPUT" && t.type === "text" || t.tagName === "SELECT" || t.tagName === "TEXTAREA")) return;
  if (ev.key === "?") { openGuide(); ev.preventDefault(); }
  else if (ev.key === "j" || ev.key === "ArrowRight") { go(1); ev.preventDefault(); }
  else if (ev.key === "k" || ev.key === "ArrowLeft") { go(-1); ev.preventDefault(); }
  else if (ev.key === "u") { nextTodo(); ev.preventDefault(); }
  else if (/^[1-9]$/.test(ev.key) && isBriefed()) {
    const item = DATA.items[idx];
    const row = item.rows[firstOpenRow(item)];
    const choice = choicesFor(row)[Number(ev.key) - 1];
    if (choice) setLabel(row, choice);
  }
});
function tick() {
  const session = Math.floor((Date.now() - sessionStart) / 60000);
  const since = Math.floor((Date.now() - breakFrom) / 60000);
  if (since >= 35) {
    $("breakText").textContent = "You have been labelling for " + since + " minutes. Take a short break: label quality drops with fatigue (safety rule 4). Download the CSV first.";
    $("breakBanner").hidden = false;
  }
  $("status").title = "Session: " + session + " min";
}
$("breakDone").addEventListener("click", () => { breakFrom = Date.now(); $("breakBanner").hidden = true; });
$("guideBtn").addEventListener("click", openGuide);
$("summaryBtn").addEventListener("click", openSummary);
$("prev").addEventListener("click", () => go(-1));
$("next").addEventListener("click", () => go(1));
$("nextTodo").addEventListener("click", nextTodo);
$("download").addEventListener("click", download);
for (const [name, help] of DATA.fields) { $("fieldList").appendChild(el("dt", name)); $("fieldList").appendChild(el("dd", help)); }
if (DATA.round >= 2) {
  $("round2").textContent = "Round 2: label without looking at your round 1 labels. Label an item only if its round 1 label is at least " + DATA.round2Days + " days old, and put today's date in the notes.";
  $("round2").hidden = false;
}
loadSaved();
setInterval(tick, 30000);
if (DATA.items.length) { render(true); if (!isBriefed()) openGuide(); }
else { $("packet").textContent = "No items for this kind and round."; }
</script>
</body>
</html>
"""
