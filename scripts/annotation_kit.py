#!/usr/bin/env python
"""Validation kit for proposal P-01: build samples, write label sheets, score labels.

Usage:
    python scripts/annotation_kit.py sample                     # stratified ID lists (committed)
    python scripts/annotation_kit.py sheet --rater jd --round 1  # label CSVs + reading packets
    python scripts/annotation_kit.py ui --rater jd --round 1     # local HTML labelling pages
    python scripts/annotation_kit.py import <downloaded.csv>    # validate and save labels
    python scripts/annotation_kit.py status                     # labelling progress
    python scripts/annotation_kit.py score                      # precision, recall, agreement, FMEA

Safety: dataset text is only read and shown as indented excerpts in gitignored
reading packets. Nothing from the dataset is executed, imported, or fetched.
See docs/validation/README.md.
"""

from __future__ import annotations

import argparse
import difflib
import hashlib
import json
import math
import re
import sys
from datetime import UTC, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

from msr_pipeline import label_ui  # noqa: E402
from msr_pipeline import validation as v  # noqa: E402
from msr_pipeline.config import Paths, get_paths, gitskills_db_path, repo_root  # noqa: E402
from msr_pipeline.load import DatasetNotFoundError, query_gitskills  # noqa: E402
from msr_pipeline.skill_risk import (  # noqa: E402
    DEFAULT_RULES_PATH,
    HIGH_RISK_SEVERITY,
    family_pairs,
    load_rules,
    read_rule_file,
    scan_contents,
    validation_sample,
)

BANNER = "> **Read only. Do not run anything in this excerpt.**"
EXCERPT_CHARS = 400
MAX_MATCHES_PER_RULE = 3
DIFF_LINES = 200
FULL_TEXT_LINES = 150


# ---------------------------------------------------------------------------
# Paths and data access
# ---------------------------------------------------------------------------


def annotations_dir(paths: Paths) -> Path:
    return paths.DATA / "annotations"


def samples_dir(paths: Paths) -> Path:
    return annotations_dir(paths) / "samples"


def work_dir(paths: Paths) -> Path:
    return annotations_dir(paths) / "work"


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def _read_csv(path: Path) -> pd.DataFrame:
    return pd.read_csv(path, dtype=str, keep_default_na=False)


def _load_reps(db: Path, shas: list[str] | None = None) -> pd.DataFrame:
    base = (
        "SELECT file_sha, name, content, first_commit_at FROM artifacts "
        "WHERE dedup_primary = 1 AND content IS NOT NULL"
    )
    if shas is None:
        return query_gitskills(base + " ORDER BY file_sha", db)
    frames = []
    for i in range(0, len(shas), 500):
        chunk = shas[i : i + 500]
        marks = ",".join("?" * len(chunk))
        frames.append(query_gitskills(f"{base} AND file_sha IN ({marks})", db, tuple(chunk)))
    if not frames:
        return pd.DataFrame(columns=["file_sha", "name", "content", "first_commit_at"])
    return pd.concat(frames, ignore_index=True)


def _as_bool(series: pd.Series) -> pd.Series:
    return series.astype(str).str.strip().str.lower().isin({"true", "1", "yes"})


def _pairs_from_results(paths: Paths, name: str) -> pd.DataFrame | None:
    path = paths.RESULTS / name
    if not path.exists():
        return None
    df = _read_csv(path)
    if not {"file_sha_a", "file_sha_b"} <= set(df.columns):
        return None
    return df


def _pair_id(a: str, b: str) -> str:
    return f"{a}|{b}"


# ---------------------------------------------------------------------------
# sample
# ---------------------------------------------------------------------------


def cmd_sample(args: argparse.Namespace) -> int:
    paths = get_paths()
    out = samples_dir(paths)
    manifest_path = out / "SAMPLE_MANIFEST.json"
    if manifest_path.exists() and not args.force:
        print(
            f"{manifest_path} already exists. Re-sampling would invalidate existing labels; "
            "pass --force only if no labelling has started.",
            file=sys.stderr,
        )
        return 1
    db = gitskills_db_path(paths)
    rules = load_rules()
    try:
        reps = _load_reps(db)
    except DatasetNotFoundError as exc:
        print(str(exc), file=sys.stderr)
        return 1
    print(f"scanning {len(reps)} distinct contents...")
    scan = scan_contents(reps, rules)

    signals = validation_sample(
        scan, n_per_category=args.per_category, n_negative=args.negatives, seed=args.seed
    )[["file_sha", "stratum", "rule_ids"]]

    lineage_all = _pairs_from_results(paths, "rq3_lineage_pairs.csv")
    differing = _pairs_from_results(paths, "rq3_differing_pairs.csv")
    pair_source = "results/rq3_*_pairs.csv"
    if lineage_all is None or differing is None:
        pairs = family_pairs(reps, scan, min_similarity=0.5)
        pairs = pairs.astype({"similarity": float})
        lineage_all = pairs
        differing = pairs[pairs["differs"].astype(bool)]
        pair_source = "recomputed with skill_risk.family_pairs (threshold 0.5)"
    else:
        if "differs" in lineage_all.columns:
            lineage_all = lineage_all.assign(differs=_as_bool(lineage_all["differs"]))

    diff_ids = {
        _pair_id(a, b)
        for a, b in zip(differing["file_sha_a"], differing["file_sha_b"], strict=True)
    }
    pair_cols = ["file_sha_a", "file_sha_b", "similarity"]
    keep = [
        _pair_id(a, b) not in diff_ids
        for a, b in zip(lineage_all["file_sha_a"], lineage_all["file_sha_b"], strict=True)
    ]
    rest = lineage_all[pd.Series(keep, index=lineage_all.index, dtype=bool)]
    random_pairs = rest.sample(n=min(args.lineage, len(rest)), random_state=args.seed)
    lineage = pd.concat(
        [
            differing[pair_cols].assign(source="differing"),
            random_pairs[pair_cols].assign(source="random"),
        ],
        ignore_index=True,
    )
    drift_cols = [
        c
        for c in ["file_sha_a", "file_sha_b", "similarity", "ordered", "only_in_a", "only_in_b"]
        if c in differing.columns
    ]
    drift = differing[drift_cols].reset_index(drop=True)

    rng = np.random.default_rng(args.seed)
    intra_rows = []
    items = {
        "signals": signals["file_sha"].tolist(),
        "lineage": [
            _pair_id(a, b)
            for a, b in zip(lineage["file_sha_a"], lineage["file_sha_b"], strict=True)
        ],
        "drift": [
            _pair_id(a, b) for a, b in zip(drift["file_sha_a"], drift["file_sha_b"], strict=True)
        ],
    }
    for kind, ids in items.items():
        if not ids:
            continue
        k = max(1, math.ceil(args.intra_share * len(ids)))
        for item in rng.choice(ids, size=min(k, len(ids)), replace=False):
            intra_rows.append({"kind": kind, "item_id": str(item)})
    intra = pd.DataFrame(intra_rows, columns=["kind", "item_id"])

    out.mkdir(parents=True, exist_ok=True)
    signals.to_csv(out / "signals_sample.csv", index=False)
    lineage.to_csv(out / "lineage_sample.csv", index=False)
    drift.to_csv(out / "drift_sample.csv", index=False)
    intra.to_csv(out / "intra_rater_subset.csv", index=False)

    rule_path = repo_root() / DEFAULT_RULES_PATH
    dataset_manifest = paths.SAMPLES / "MANIFEST.json"
    db_sha = None
    if dataset_manifest.exists():
        for entry in json.loads(dataset_manifest.read_text(encoding="utf-8")).get("files", []):
            if str(entry.get("file", "")).replace("\\", "/").endswith(db.name):
                db_sha = entry.get("sha256")
    manifest = {
        "created_at": datetime.now(UTC).isoformat(timespec="seconds"),
        "seed": args.seed,
        "parameters": {
            "per_category": args.per_category,
            "negatives": args.negatives,
            "lineage_random_pairs": args.lineage,
            "intra_share": args.intra_share,
            "high_risk_severity": HIGH_RISK_SEVERITY,
        },
        "rule_file": str(DEFAULT_RULES_PATH).replace("\\", "/"),
        "rule_file_sha256": _sha256(rule_path),
        "dataset_sha256": db_sha,
        "pair_source": pair_source,
        "population": {
            "distinct_contents": int(len(scan)),
            "high_risk_contents": int(scan["high_risk"].sum()),
            "no_signal_contents": int((scan["rule_ids"] == "").sum()),
            "lineage_pairs": int(len(lineage_all)),
            "differing_pairs": int(len(differing)),
        },
        "sizes": {
            "signals_items": int(len(signals)),
            "signals_no_signal_items": int((signals["stratum"] == "NO_SIGNAL").sum()),
            "lineage_pairs": int(len(lineage)),
            "drift_pairs": int(len(drift)),
            "intra_rater_items": {k: int((intra["kind"] == k).sum()) for k in v.KINDS},
        },
    }
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(manifest["sizes"], indent=2))
    print(f"wrote samples to {out}")
    return 0


# ---------------------------------------------------------------------------
# sheet
# ---------------------------------------------------------------------------


def _load_samples(paths: Paths) -> dict[str, pd.DataFrame]:
    d = samples_dir(paths)
    needed = [
        "signals_sample.csv",
        "lineage_sample.csv",
        "drift_sample.csv",
        "intra_rater_subset.csv",
    ]
    missing = [n for n in needed if not (d / n).exists()]
    if missing:
        raise FileNotFoundError(
            f"missing {missing} in {d}; run `python scripts/annotation_kit.py sample` first"
        )
    return {
        "signals": _read_csv(d / "signals_sample.csv"),
        "lineage": _read_csv(d / "lineage_sample.csv"),
        "drift": _read_csv(d / "drift_sample.csv"),
        "intra": _read_csv(d / "intra_rater_subset.csv"),
        "manifest": json.loads((d / "SAMPLE_MANIFEST.json").read_text(encoding="utf-8"))
        if (d / "SAMPLE_MANIFEST.json").exists()
        else {},
    }


def signal_keys(signals: pd.DataFrame, rules) -> pd.DataFrame:
    """One label row per high-risk rule match, or one NONE row per NO_SIGNAL item."""
    severity = {r.id: r.severity for r in rules}
    rows = []
    for rec in signals.to_dict("records"):
        if rec["stratum"] == "NO_SIGNAL":
            rows.append({"file_sha": rec["file_sha"], "rule_id": v.NONE_RULE})
            continue
        for rid in [x for x in rec["rule_ids"].split(";") if x]:
            if severity.get(rid, 0) >= HIGH_RISK_SEVERITY:
                rows.append({"file_sha": rec["file_sha"], "rule_id": rid})
    return pd.DataFrame(rows, columns=["file_sha", "rule_id"]).drop_duplicates()


def _neutralise(text: str, max_chars: int | None = None) -> str:
    if max_chars is not None and len(text) > max_chars:
        text = text[:max_chars] + " [truncated]"
    text = text.replace("```", "'''").replace("~~~", "'''")
    return "\n".join("    " + line for line in text.splitlines()) or "    (empty)"


def _excerpts(content: str, rule) -> list[str]:
    lines = content.splitlines()
    out = []
    seen_lines: set[int] = set()
    for pattern in rule.patterns:
        for match in pattern.finditer(content):
            line_no = content.count("\n", 0, match.start()) + 1
            if line_no in seen_lines:
                continue
            seen_lines.add(line_no)
            start, end = max(0, line_no - 4), min(len(lines), line_no + 3)
            snippet = "\n".join(lines[start:end])
            out.append(f"Line {line_no}:\n\n{_neutralise(snippet, EXCERPT_CHARS)}")
            if len(out) >= MAX_MATCHES_PER_RULE:
                return out
    return out


def _signal_packet(index: int, rec: dict, content_row: dict | None, rules_by_id: dict) -> str:
    name = (content_row or {}).get("name") or ""
    parts = [
        f"# Signal item {index:03d}",
        "",
        BANNER,
        "",
        f"- file_sha: `{rec['file_sha']}`",
        f"- front-matter name: {name if isinstance(name, str) else ''}",
        f"- stratum: {rec['stratum']}",
        f"- matched rules: {rec['rule_ids'] or 'none'}",
        "",
    ]
    content = (content_row or {}).get("content")
    if not isinstance(content, str):
        return "\n".join(parts + ["Content not found in the sample database.", ""])
    if rec["stratum"] == "NO_SIGNAL":
        lines = content.splitlines()
        shown = "\n".join(line[:300] for line in lines[:FULL_TEXT_LINES])
        parts += [
            "No rule matched. Read the text and label NONE_PRESENT, or MISSED_RISKY "
            "with the missed category.",
            "",
            _neutralise(shown),
        ]
        if len(lines) > FULL_TEXT_LINES:
            parts.append(f"\n[{len(lines) - FULL_TEXT_LINES} more lines not shown]")
        return "\n".join(parts) + "\n"
    for rid in [x for x in rec["rule_ids"].split(";") if x]:
        rule = rules_by_id.get(rid)
        if rule is None:
            continue
        label_hint = (
            "label this rule"
            if rule.severity >= HIGH_RISK_SEVERITY
            else "context only, no label row"
        )
        parts += [
            f"## {rid} ({rule.category}, severity {rule.severity}; {label_hint})",
            "",
            f"Rule note: {rule.note}",
            "",
        ]
        for ex in _excerpts(content, rule):
            parts += [ex, ""]
    return "\n".join(parts) + "\n"


def _pair_packet(kind: str, index: int, rec: dict, contents: dict[str, dict]) -> str:
    a, b = contents.get(rec["file_sha_a"], {}), contents.get(rec["file_sha_b"], {})
    parts = [
        f"# {kind.capitalize()} pair {index:03d}",
        "",
        BANNER,
        "",
        f"- file_sha_a: `{rec['file_sha_a']}`",
        f"- file_sha_b: `{rec['file_sha_b']}`",
        f"- front-matter names: {a.get('name') or ''} / {b.get('name') or ''}",
        f"- similarity: {rec.get('similarity', '')}",
    ]
    for key in ("source", "ordered", "only_in_a", "only_in_b"):
        if key in rec:
            parts.append(f"- {key}: {rec[key]}")
    text_a, text_b = a.get("content"), b.get("content")
    if not isinstance(text_a, str) or not isinstance(text_b, str):
        return "\n".join(parts + ["", "Content not found in the sample database.", ""])
    diff = list(
        difflib.unified_diff(text_a.splitlines(), text_b.splitlines(), "a", "b", n=2, lineterm="")
    )
    truncated = len(diff) > DIFF_LINES
    shown = "\n".join(line[:300] for line in diff[:DIFF_LINES]) or "(identical text)"
    parts += ["", "Unified diff, a to b:", "", _neutralise(shown)]
    if truncated:
        parts.append(f"\n[{len(diff) - DIFF_LINES} more diff lines not shown]")
    return "\n".join(parts) + "\n"


def cmd_sheet(args: argparse.Namespace) -> int:
    paths = get_paths()
    try:
        label_filename = {k: v.label_filename(k, args.rater, args.round) for k in v.KINDS}
        samples = _load_samples(paths)
    except (ValueError, FileNotFoundError) as exc:
        print(str(exc), file=sys.stderr)
        return 1
    rules = load_rules()
    rules_by_id = {r.id: r for r in rules}
    kinds = [args.kind] if args.kind else list(v.KINDS)
    seed = int(samples["manifest"].get("seed", 580))
    intra = samples["intra"]
    ann = annotations_dir(paths)
    ann.mkdir(parents=True, exist_ok=True)
    db = gitskills_db_path(paths)

    for kind in kinds:
        items = samples[kind].copy()
        if kind == "signals":
            item_ids = items["file_sha"]
        else:
            item_ids = pd.Series(
                [
                    _pair_id(a, b)
                    for a, b in zip(items["file_sha_a"], items["file_sha_b"], strict=True)
                ],
                index=items.index,
            )
        if args.round >= 2:
            subset = set(intra.loc[intra["kind"] == kind, "item_id"])
            items = items[item_ids.isin(subset)]
            items = items.sample(frac=1.0, random_state=seed + args.round) if len(items) else items
        items = items.reset_index(drop=True)

        if kind == "signals":
            keys = signal_keys(items, rules)
        else:
            keys = items[["file_sha_a", "file_sha_b"]]
        label_path = ann / label_filename[kind]
        if label_path.exists():
            print(f"{label_path} exists; not overwritten")
        else:
            v.blank_labels(kind, keys).to_csv(label_path, index=False)
            print(f"wrote {label_path} ({len(keys)} rows)")

        shas = (
            items["file_sha"].tolist()
            if kind == "signals"
            else sorted(set(items["file_sha_a"]) | set(items["file_sha_b"]))
        )
        try:
            contents = (
                {r["file_sha"]: r for r in _load_reps(db, shas).to_dict("records")} if shas else {}
            )
        except DatasetNotFoundError as exc:
            print(f"{exc} Reading packets skipped.", file=sys.stderr)
            continue
        packet_dir = work_dir(paths) / f"{kind}_{args.rater}_r{args.round}"
        packet_dir.mkdir(parents=True, exist_ok=True)
        index_lines = [
            f"# {kind} packets for rater {args.rater}, round {args.round}",
            "",
            BANNER,
            "",
        ]
        for i, rec in enumerate(items.to_dict("records"), start=1):
            if kind == "signals":
                fname = f"{i:03d}_{rec['file_sha'][:12]}.md"
                text = _signal_packet(i, rec, contents.get(rec["file_sha"]), rules_by_id)
            else:
                fname = f"{i:03d}_{rec['file_sha_a'][:8]}_{rec['file_sha_b'][:8]}.md"
                text = _pair_packet(kind, i, rec, contents)
            (packet_dir / fname).write_text(text, encoding="utf-8")
            index_lines.append(f"- [{fname}]({fname})")
        (packet_dir / "INDEX.md").write_text("\n".join(index_lines) + "\n", encoding="utf-8")
        print(f"wrote {len(items)} reading packets to {packet_dir}")
    return 0


# ---------------------------------------------------------------------------
# status and score
# ---------------------------------------------------------------------------


def cmd_status(_: argparse.Namespace) -> int:
    paths = get_paths()
    d = samples_dir(paths)
    manifest = d / "SAMPLE_MANIFEST.json"
    if manifest.exists():
        sizes = json.loads(manifest.read_text(encoding="utf-8")).get("sizes", {})
        print("Sample sizes:")
        for key, value in sizes.items():
            print(f"  {key}: {value}")
    else:
        print("No sample yet. Run `python scripts/annotation_kit.py sample`.")
    files = v.discover_label_files(annotations_dir(paths))
    if not files:
        print(
            "No label files yet. Run "
            "`python scripts/annotation_kit.py sheet --rater <id> --round 1`."
        )
        return 0
    print("Label files:")
    for f in files:
        df = v.read_label_csv(f.path)
        done = len(v.labelled_rows(df, f.kind))
        who = "human" if f.is_human else "non-human (llm)"
        cov = v.justification_coverage(df, f.kind)
        reason = ""
        if cov["owed"]:
            reason = f"; reasons {cov['given']}/{cov['owed']}"
            if cov["missing"]:
                reason += f" ({cov['missing']} MISSING)"
        print(f"  {f.name}: {done}/{len(df)} rows labelled ({who}){reason}")
    return 0


PROPOSALS_HEADER = """# Rule change proposals

Generated by `python scripts/annotation_kit.py proposals`. One section per rule
that the signal labels show misfiring, newest run overwrites the counts.

A false positive is a rule row labelled `NOT_PRESENT` (the match is not the
capability at all) or `BENIGN_CONTEXT` (the capability is there but the context
makes it low risk). `NOT_PRESENT` is the stronger signal that the *pattern* is
wrong; `BENIGN_CONTEXT` usually means the pattern is right but needs context.

Counts come from labels. The two prose lines under each rule are written by the
rater and are **not** generated: fill in why it misfires and what you would
change. Anything still reading TODO has not been decided yet.

Do not edit a label file to make a rule look better. Proposals become issues and
are applied in a later round, and the report says which round produced which
numbers.
"""


def cmd_proposals(args: argparse.Namespace) -> int:
    """Aggregate signal false positives by rule to seed rule change proposals."""
    paths = get_paths()
    out = (
        Path(args.out)
        if getattr(args, "out", None)
        else repo_root() / "docs" / "validation" / "RULE_CHANGE_PROPOSALS.md"
    )
    files = [
        f for f in v.discover_label_files(annotations_dir(paths))
        if f.kind == "signals" and (args.include_llm or f.is_human)
    ]
    if not files:
        print("No signals label files yet.")
        return 1

    existing = out.read_text(encoding="utf-8") if out.exists() else ""
    kept: dict[str, tuple[str, str]] = {}
    for block in re.split(r"^## ", existing, flags=re.M)[1:]:
        rule = block.split(None, 1)[0].strip()
        why = re.search(r"^Why it misfires:\s*(.*)$", block, re.M)
        would = re.search(r"^What I would do:\s*(.*)$", block, re.M)
        kept[rule] = (
            (why.group(1).strip() if why else "TODO"),
            (would.group(1).strip() if would else "TODO"),
        )

    per_rule: dict[str, dict] = {}
    for f in files:
        df = v.read_label_csv(f.path)
        rows = v.valid_labelled_rows(df, "signals")
        rows = rows[rows["rule_id"].astype(str).str.strip() != v.NONE_RULE]
        for rec in rows.to_dict("records"):
            rule = str(rec["rule_id"]).strip()
            label = str(rec["label"]).strip()
            d = per_rule.setdefault(
                rule, {"matches": 0, "fp": 0, "evidence": [], "by_label": {}}
            )
            d["matches"] += 1
            d["by_label"][label] = d["by_label"].get(label, 0) + 1
            if label in ("NOT_PRESENT", "BENIGN_CONTEXT"):
                d["fp"] += 1
                note = str(rec.get("notes", "") or "").strip()
                d["evidence"].append((str(rec["file_sha"])[:8], label, note))

    misfiring = {r: d for r, d in per_rule.items() if d["fp"]}
    lines = [PROPOSALS_HEADER]
    if not misfiring:
        lines.append(
            "\nNo false positives labelled yet. Label some signal rows, then rerun.\n"
        )
    for rule in sorted(misfiring, key=lambda r: (-misfiring[r]["fp"], r)):
        d = misfiring[rule]
        precision = 1 - d["fp"] / d["matches"] if d["matches"] else 0.0
        why, would = kept.get(rule, ("TODO", "TODO"))
        lines.append(f"\n## {rule}\n")
        lines.append(
            f"Labelled matches: {d['matches']} | false positives: {d['fp']} "
            f"| observed precision: {precision:.2f}\n"
        )
        spread = ", ".join(f"{k}={n}" for k, n in sorted(d["by_label"].items()))
        lines.append(f"Label spread: {spread}\n")
        lines.append(f"\nWhy it misfires: {why}\n")
        lines.append(f"What I would do: {would}\n")
        lines.append("\nEvidence rows:\n\n")
        for sha, label, note in d["evidence"][: args.max_evidence]:
            lines.append(f"- `{sha}` {label}: {note or '(no reason recorded)'}\n")
        if len(d["evidence"]) > args.max_evidence:
            lines.append(f"- ... and {len(d['evidence']) - args.max_evidence} more\n")

    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("".join(lines), encoding="utf-8", newline="\n")
    total_fp = sum(d["fp"] for d in misfiring.values())
    print(f"Wrote {out}")
    print(f"  rules with false positives: {len(misfiring)}; false positives: {total_fp}")
    if kept:
        print(f"  kept prose for {len(kept)} rule(s) already written up")
    return 0


def _primary(
    files: list[tuple[v.LabelFile, pd.DataFrame]], kind: str
) -> tuple[v.LabelFile, pd.DataFrame] | None:
    """Human, lowest round, most labelled rows; ties broken by rater id."""
    candidates = [(f, df) for f, df in files if f.kind == kind and f.is_human]
    if not candidates:
        return None
    lowest = min(f.round for f, _ in candidates)
    candidates = [(f, df) for f, df in candidates if f.round == lowest]
    return sorted(candidates, key=lambda x: (-len(v.labelled_rows(x[1], kind)), x[0].rater))[0]


def cmd_score(_: argparse.Namespace) -> int:
    paths = get_paths()
    files = v.discover_label_files(annotations_dir(paths))
    if not files:
        print(
            "No label files found in data/annotations/. Next steps:\n"
            "  1. python scripts/annotation_kit.py sample\n"
            "  2. python scripts/annotation_kit.py sheet --rater jd --round 1\n"
            "  3. Fill the label CSVs using docs/validation/ANNOTATION_GUIDELINE.md\n"
            "  4. python scripts/annotation_kit.py score"
        )
        return 0
    rules = load_rules()
    rule_file = read_rule_file()
    rule_ids = [r.id for r in rules]
    categories = list((rule_file.get("categories") or {}).keys())

    loaded: list[tuple[v.LabelFile, pd.DataFrame]] = []
    problems: list[str] = []
    for f in files:
        df = v.read_label_csv(f.path)
        problems += v.validate_labels(df, f.kind, rule_ids, categories, source=f.name)
        if all(c in df.columns for c in v.KIND_COLUMNS[f.kind]):
            loaded.append((f, df))
    if not any(len(v.labelled_rows(df, f.kind)) for f, df in loaded):
        print(
            "Label files exist but no rows are labelled yet, so nothing was written. "
            "Fill the label column using docs/validation/ANNOTATION_GUIDELINE.md, then score again."
        )
        for p in problems:
            print(f"  - {p}", file=sys.stderr)
        return 2 if problems else 0
    if problems:
        print(
            f"{len(problems)} label problem(s); invalid rows are left out of the scores:",
            file=sys.stderr,
        )
        for p in problems:
            print(f"  - {p}", file=sys.stderr)

    empty_signals = pd.DataFrame(columns=v.KIND_COLUMNS["signals"])
    primary_signals = _primary(loaded, "signals")
    signal_df = primary_signals[1] if primary_signals else empty_signals
    by_rule = v.precision_by_rule(signal_df, rules)
    by_category = v.precision_by_category(signal_df, rules)

    manifest_path = samples_dir(paths) / "SAMPLE_MANIFEST.json"
    manifest = (
        json.loads(manifest_path.read_text(encoding="utf-8")) if manifest_path.exists() else {}
    )
    stratum_size = int(manifest.get("sizes", {}).get("signals_no_signal_items", 0))
    population = int(manifest.get("population", {}).get("no_signal_contents", 0))
    recall = v.recall_estimate(signal_df, stratum_size, population)

    agree = v.agreement(loaded)
    primary_lineage = _primary(loaded, "lineage")
    lineage = v.lineage_precision(
        primary_lineage[1] if primary_lineage else pd.DataFrame(columns=v.KIND_COLUMNS["lineage"])
    )
    primary_drift = _primary(loaded, "drift")
    drift = v.drift_distribution(
        primary_drift[1] if primary_drift else pd.DataFrame(columns=v.KIND_COLUMNS["drift"])
    )

    for prev_name in ("rq1_prevalence_by_category.csv", "pilot_skill_risk_categories.csv"):
        prev_path = paths.RESULTS / prev_name
        if prev_path.exists():
            prevalence = pd.read_csv(prev_path)
            break
    else:
        prevalence = pd.DataFrame(columns=["category", "contents", "content_share"])
        print("No prevalence table found; FMEA occurrence scores will be 1.", file=sys.stderr)
    fmea = v.fmea_ranking(prevalence, by_category, recall, rules)

    source = {
        "signals": primary_signals[0].name if primary_signals else "",
        "lineage": primary_lineage[0].name if primary_lineage else "",
        "drift": primary_drift[0].name if primary_drift else "",
    }
    outputs = {
        "validation_precision_by_rule": by_rule.assign(label_file=source["signals"]),
        "validation_precision_by_category": by_category.assign(label_file=source["signals"]),
        "validation_recall": recall.assign(label_file=source["signals"]),
        "validation_agreement": agree,
        "validation_lineage": lineage.assign(label_file=source["lineage"]),
        "validation_drift": drift.assign(label_file=source["drift"]),
        "fmea_category_ranking": fmea,
    }
    paths.RESULTS.mkdir(parents=True, exist_ok=True)
    for name, df in outputs.items():
        path = paths.RESULTS / f"{name}.csv"
        df.to_csv(path, index=False)
        print(f"wrote {path}")
    return 2 if problems else 0


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def cmd_ui(args: argparse.Namespace) -> int:
    """Write one local HTML labelling page per kind from the label sheet and packets."""
    paths = get_paths()
    try:
        filenames = {k: v.label_filename(k, args.rater, args.round) for k in v.KINDS}
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        return 1
    categories = list((read_rule_file().get("categories") or {}).keys())
    ann = annotations_dir(paths)
    kinds = [args.kind] if args.kind else list(v.KINDS)
    written = 0
    for kind in kinds:
        label_path = ann / filenames[kind]
        if not label_path.exists():
            print(
                f"{label_path} not found; run `annotation_kit.py sheet --rater {args.rater} "
                f"--round {args.round}` first",
                file=sys.stderr,
            )
            continue
        labels = v.read_label_csv(label_path)
        packet_dir = work_dir(paths) / f"{kind}_{args.rater}_r{args.round}"
        items = label_ui.build_items(kind, labels, label_ui.read_packets(packet_dir, kind))
        page = work_dir(paths) / f"label_{kind}_{args.rater}_r{args.round}.html"
        page.parent.mkdir(parents=True, exist_ok=True)
        page.write_text(
            label_ui.build_html(kind, args.rater, args.round, items, categories),
            encoding="utf-8",
        )
        missing = sum(1 for i in items if i["packet"].startswith("Reading packet not found"))
        note = f", {missing} without packets" if missing else ""
        print(f"wrote {page} ({len(items)} items, {len(labels)} label rows{note})")
        written += 1
    return 0 if written else 1


def cmd_import(args: argparse.Namespace) -> int:
    """Validate a label CSV downloaded from the labelling page and save it."""
    paths = get_paths()
    src = Path(args.file)
    if not src.exists():
        print(f"{src} not found", file=sys.stderr)
        return 1
    rules = load_rules()
    categories = list((read_rule_file().get("categories") or {}).keys())
    target, problems, labelled = label_ui.import_labels(
        src, annotations_dir(paths), [r.id for r in rules], categories, replace=args.replace
    )
    if problems:
        for problem in problems:
            print(problem, file=sys.stderr)
        return 1
    print(f"imported {labelled} labelled rows into {target}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    sub = parser.add_subparsers(dest="command", required=True)

    p = sub.add_parser("sample", help="Build stratified ID samples (committed, IDs only).")
    p.add_argument("--seed", type=int, default=580)
    p.add_argument("--per-category", type=int, default=10)
    p.add_argument("--negatives", type=int, default=40)
    p.add_argument(
        "--lineage", type=int, default=40, help="Random lineage pairs added to all differing pairs."
    )
    p.add_argument("--intra-share", type=float, default=0.3)
    p.add_argument("--force", action="store_true", help="Replace an existing sample.")
    p.set_defaults(func=cmd_sample)

    p = sub.add_parser("sheet", help="Write blank label CSVs and reading packets.")
    p.add_argument(
        "--rater", required=True, help="Short id, e.g. jd; prefix llm- for a non-human rater."
    )
    p.add_argument("--round", type=int, default=1)
    p.add_argument("--kind", choices=v.KINDS, default=None)
    p.set_defaults(func=cmd_sheet)

    p = sub.add_parser("status", help="Show labelling progress.")
    p.set_defaults(func=cmd_status)

    p = sub.add_parser("score", help="Score label files into results/validation_*.csv.")
    p.set_defaults(func=cmd_score)

    p = sub.add_parser("ui", help="Write local HTML labelling pages (gitignored).")
    p.add_argument("--rater", required=True, help="Short id, e.g. jd.")
    p.add_argument("--round", type=int, default=1)
    p.add_argument("--kind", choices=v.KINDS, default=None)
    p.set_defaults(func=cmd_ui)

    p = sub.add_parser("import", help="Validate a downloaded label CSV and save it.")
    p.add_argument("file", help="CSV downloaded from the labelling page.")
    p.add_argument("--replace", action="store_true", help="Overwrite labels that differ.")
    p.set_defaults(func=cmd_import)

    p = sub.add_parser(
        "proposals",
        help="Aggregate signal false positives by rule into RULE_CHANGE_PROPOSALS.md.",
    )
    p.add_argument(
        "--include-llm",
        action="store_true",
        help="Also count non-human (llm-) raters. Off by default.",
    )
    p.add_argument("--max-evidence", type=int, default=8, help="Evidence rows per rule.")
    p.add_argument("--out", default=None, help="Write somewhere other than docs/validation/.")
    p.set_defaults(func=cmd_proposals)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    return int(args.func(args))


if __name__ == "__main__":
    raise SystemExit(main())
