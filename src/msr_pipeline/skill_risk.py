"""Pilot: rule-based risk-signal scanner for agent skills (proposal P-01).

Static text analysis only. Nothing found in the dataset is executed, imported, or
fetched. Rules live in ``rules/skill_risk_rules.yaml`` (id, category, severity,
patterns, status, source, examples) so they can be reviewed like code and validated
against annotations. A rule match is a signal, not a verdict.

The module answers three pilot questions on the GitSkills sample:

1. Prevalence: how many distinct skill contents, and how many copies of them, carry
   each risk signal (content-weighted versus copy-weighted exposure).
2. Reach: do contents with high-risk signals get copied more or less than others.
3. Variation: among near-duplicate variants that share a front-matter name, how often
   do high-risk capabilities differ, and in which direction when commit dates exist.
"""

from __future__ import annotations

import re
import zlib
from collections.abc import Iterable
from dataclasses import dataclass
from itertools import combinations
from pathlib import Path

import pandas as pd
import yaml

from .config import Paths, get_paths, repo_root

DEFAULT_RULES_PATH = Path("rules") / "skill_risk_rules.yaml"
HIGH_RISK_SEVERITY = 6
SCRIPT_EXTENSIONS = (
    ".sh",
    ".bash",
    ".zsh",
    ".ps1",
    ".py",
    ".js",
    ".mjs",
    ".cjs",
    ".ts",
    ".rb",
    ".pl",
    ".bat",
    ".cmd",
)
SCAN_COLUMNS = [
    "file_sha",
    "name",
    "first_commit_at",
    "rule_ids",
    "categories",
    "high_risk_categories",
    "max_severity",
    "high_risk",
]
PAIR_COLUMNS = [
    "family",
    "file_sha_a",
    "file_sha_b",
    "similarity",
    "ordered",
    "only_in_a",
    "only_in_b",
    "differs",
]


@dataclass(frozen=True)
class Rule:
    id: str
    category: str
    severity: int
    patterns: tuple[re.Pattern[str], ...]
    status: str = "active"
    source: str = "expert"
    note: str = ""

    def matches(self, text: str) -> bool:
        return any(p.search(text) for p in self.patterns)


# ---------------------------------------------------------------------------
# Rules
# ---------------------------------------------------------------------------


def rules_from_dict(data: dict, include_inactive: bool = False) -> list[Rule]:
    """Validate a parsed rule file and compile its patterns."""
    categories = set((data.get("categories") or {}).keys())
    rules: list[Rule] = []
    seen: set[str] = set()
    for raw in data.get("rules") or []:
        rid = str(raw["id"])
        if rid in seen:
            raise ValueError(f"duplicate rule id {rid}")
        seen.add(rid)
        category = str(raw["category"])
        if categories and category not in categories:
            raise ValueError(f"rule {rid}: unknown category {category}")
        severity = int(raw["severity"])
        if not 1 <= severity <= 10:
            raise ValueError(f"rule {rid}: severity {severity} outside 1..10")
        status = str(raw.get("status", "active"))
        if status != "active" and not include_inactive:
            continue
        flags = re.MULTILINE | (0 if raw.get("case_sensitive") else re.IGNORECASE)
        patterns = tuple(re.compile(p, flags) for p in raw["patterns"])
        rules.append(
            Rule(
                id=rid,
                category=category,
                severity=severity,
                patterns=patterns,
                status=status,
                source=str(raw.get("source", "expert")),
                note=str(raw.get("note", "")),
            )
        )
    return rules


def read_rule_file(path: Path | str | None = None) -> dict:
    path = Path(path) if path else repo_root() / DEFAULT_RULES_PATH
    return yaml.safe_load(path.read_text(encoding="utf-8")) or {}


def load_rules(path: Path | str | None = None, include_inactive: bool = False) -> list[Rule]:
    return rules_from_dict(read_rule_file(path), include_inactive)


def scan_text(text: str | None, rules: Iterable[Rule]) -> list[str]:
    """Return the ids of rules that match ``text``."""
    if not text:
        return []
    return [r.id for r in rules if r.matches(text)]


def _text(value: object) -> str:
    """Strings pass through; None, NaN, and other values become ""."""
    return value if isinstance(value, str) else ""


def _split(value: str | None) -> list[str]:
    return [x for x in (value or "").split(";") if x]


_PATH_LIKE = re.compile(r"^[\w./ -]+$")


def is_symlink_stub(content: object) -> bool:
    """True when content is a single short path-like line (a symlink target, not a skill)."""
    text = _text(content).strip()
    if not text or "\n" in text or len(text) >= 200:
        return False
    if not _PATH_LIKE.match(text):
        return False
    return "/" in text or text.lower().endswith(".md")


def population_flags(reps: pd.DataFrame) -> pd.DataFrame:
    """Per distinct content: has_content, is_symlink_stub, frontmatter_valid, in_main_population."""
    contents = reps["content"] if "content" in reps.columns else pd.Series([None] * len(reps))
    has_content = contents.map(lambda c: bool(_text(c).strip())).to_numpy()
    stub = contents.map(is_symlink_stub).to_numpy()
    if "frontmatter_valid" in reps.columns:
        fm = pd.to_numeric(reps["frontmatter_valid"], errors="coerce").fillna(0).to_numpy() == 1
    else:
        fm = [False] * len(reps)
    out = pd.DataFrame(
        {
            "file_sha": reps["file_sha"].to_numpy(),
            "has_content": has_content,
            "is_symlink_stub": stub,
            "frontmatter_valid": fm,
        }
    )
    out["in_main_population"] = out["has_content"] & ~out["is_symlink_stub"]
    return out


# ---------------------------------------------------------------------------
# Similarity
# ---------------------------------------------------------------------------

_TOKEN = re.compile(r"[a-z0-9]+")


def shingles(text: str | None, k: int = 5) -> frozenset[int]:
    """Hashed word k-shingles of lower-cased alphanumeric tokens."""
    tokens = _TOKEN.findall((text or "").lower())
    if not tokens:
        return frozenset()
    if len(tokens) < k:
        return frozenset({zlib.crc32(" ".join(tokens).encode())})
    return frozenset(
        zlib.crc32(" ".join(tokens[i : i + k]).encode()) for i in range(len(tokens) - k + 1)
    )


def jaccard(a: frozenset[int], b: frozenset[int]) -> float:
    if not a or not b:
        return 0.0
    return len(a & b) / len(a | b)


# ---------------------------------------------------------------------------
# Analyses (pure: DataFrames in, DataFrames out)
# ---------------------------------------------------------------------------


def scan_contents(
    reps: pd.DataFrame, rules: list[Rule], high_risk_severity: int = HIGH_RISK_SEVERITY
) -> pd.DataFrame:
    """Scan one row per distinct content (columns file_sha, content, name, first_commit_at)."""
    by_id = {r.id: r for r in rules}
    rows = []
    for rec in reps.to_dict("records"):
        ids = scan_text(_text(rec.get("content")), rules)
        cats = sorted({by_id[i].category for i in ids})
        high = sorted({by_id[i].category for i in ids if by_id[i].severity >= high_risk_severity})
        rows.append(
            {
                "file_sha": rec["file_sha"],
                "name": _text(rec.get("name")),
                "first_commit_at": _text(rec.get("first_commit_at")),
                "rule_ids": ";".join(ids),
                "categories": ";".join(cats),
                "high_risk_categories": ";".join(high),
                "max_severity": max((by_id[i].severity for i in ids), default=0),
                "high_risk": bool(high),
            }
        )
    return pd.DataFrame(rows, columns=SCAN_COLUMNS)


def copy_counts(occurrences: pd.DataFrame) -> pd.DataFrame:
    """Copies and distinct repositories per content (columns file_sha, repo_full_name)."""
    if occurrences.empty:
        return pd.DataFrame(columns=["file_sha", "copies", "repos"])
    return (
        occurrences.groupby("file_sha")
        .agg(copies=("repo_full_name", "size"), repos=("repo_full_name", "nunique"))
        .reset_index()
    )


def _with_counts(scan: pd.DataFrame, counts: pd.DataFrame) -> pd.DataFrame:
    merged = scan.merge(counts, on="file_sha", how="left")
    merged["copies"] = merged["copies"].fillna(1).astype(int)
    merged["repos"] = merged["repos"].fillna(1).astype(int)
    return merged


def _share(part: float, whole: float) -> float:
    return round(float(part) / float(whole), 4) if whole else 0.0


def rule_prevalence(scan: pd.DataFrame, counts: pd.DataFrame, rules: list[Rule]) -> pd.DataFrame:
    """Per rule: distinct contents and copy-weighted occurrences that match."""
    merged = _with_counts(scan, counts)
    n_contents, n_occ = len(merged), int(merged["copies"].sum())
    rows = []
    for rule in rules:
        mask = merged["rule_ids"].apply(lambda s, rid=rule.id: rid in _split(s))
        occ = int(merged.loc[mask, "copies"].sum())
        rows.append(
            {
                "rule_id": rule.id,
                "category": rule.category,
                "severity": rule.severity,
                "contents": int(mask.sum()),
                "content_share": _share(mask.sum(), n_contents),
                "occurrences": occ,
                "occurrence_share": _share(occ, n_occ),
            }
        )
    high = merged["high_risk"].astype(bool)
    occ_high = int(merged.loc[high, "copies"].sum())
    rows.append(
        {
            "rule_id": "ANY_HIGH_RISK",
            "category": "ANY_HIGH_RISK",
            "severity": HIGH_RISK_SEVERITY,
            "contents": int(high.sum()),
            "content_share": _share(high.sum(), n_contents),
            "occurrences": occ_high,
            "occurrence_share": _share(occ_high, n_occ),
        }
    )
    return pd.DataFrame(rows)


def category_prevalence(
    scan: pd.DataFrame, counts: pd.DataFrame, rules: list[Rule]
) -> pd.DataFrame:
    """Per category: distinct contents and copy-weighted occurrences, sorted by share."""
    merged = _with_counts(scan, counts)
    n_contents, n_occ = len(merged), int(merged["copies"].sum())
    max_sev: dict[str, int] = {}
    for r in rules:
        max_sev[r.category] = max(max_sev.get(r.category, 0), r.severity)
    rows = []
    for cat, sev in max_sev.items():
        mask = merged["categories"].apply(lambda s, c=cat: c in _split(s))
        occ = int(merged.loc[mask, "copies"].sum())
        rows.append(
            {
                "category": cat,
                "max_rule_severity": sev,
                "contents": int(mask.sum()),
                "content_share": _share(mask.sum(), n_contents),
                "occurrences": occ,
                "occurrence_share": _share(occ, n_occ),
            }
        )
    df = pd.DataFrame(rows)
    return df.sort_values(["content_share", "category"], ascending=[False, True]).reset_index(
        drop=True
    )


def reach_by_risk(scan: pd.DataFrame, counts: pd.DataFrame) -> pd.DataFrame:
    """Copy reach of contents with and without a high-risk signal."""
    merged = _with_counts(scan, counts)
    rows = []
    for label, mask in (
        ("high-risk signal", merged["high_risk"].astype(bool)),
        ("no high-risk signal", ~merged["high_risk"].astype(bool)),
    ):
        g = merged[mask]
        rows.append(
            {
                "group": label,
                "contents": len(g),
                "occurrences": int(g["copies"].sum()),
                "mean_copies": round(float(g["copies"].mean()), 3) if len(g) else 0.0,
                "median_copies": float(g["copies"].median()) if len(g) else 0.0,
                "share_copied_2plus": _share((g["copies"] >= 2).sum(), len(g)),
                "share_cross_repo": _share((g["repos"] >= 2).sum(), len(g)),
                "max_copies": int(g["copies"].max()) if len(g) else 0,
            }
        )
    return pd.DataFrame(rows)


def _families(scan: pd.DataFrame) -> pd.Series:
    return scan["name"].fillna("").astype(str).str.strip().str.lower()


def family_pairs(
    reps: pd.DataFrame,
    scan: pd.DataFrame,
    min_similarity: float = 0.5,
    max_family_size: int = 200,
) -> pd.DataFrame:
    """Near-duplicate variant pairs within front-matter name families.

    A pair is kept when the word-shingle Jaccard similarity is at least
    ``min_similarity`` (a plausible shared lineage). When both variants have a first
    commit date, ``a`` is the older and ``b`` the newer, so ``only_in_b`` lists
    high-risk categories the newer variant added and ``only_in_a`` those it dropped.
    """
    df = scan.merge(reps[["file_sha", "content"]], on="file_sha", how="inner")
    df = df.assign(family=_families(df))
    df = df[df["family"] != ""]
    rows = []
    for family, group in df.groupby("family"):
        if len(group) < 2 or len(group) > max_family_size:
            continue
        records = group.to_dict("records")
        sh = {r["file_sha"]: shingles(_text(r["content"])) for r in records}
        for a, b in combinations(records, 2):
            sim = jaccard(sh[a["file_sha"]], sh[b["file_sha"]])
            if sim < min_similarity:
                continue
            ordered = bool(a["first_commit_at"]) and bool(b["first_commit_at"])
            ordered = ordered and a["first_commit_at"] != b["first_commit_at"]
            if ordered and a["first_commit_at"] > b["first_commit_at"]:
                a, b = b, a
            ca = set(_split(a["high_risk_categories"]))
            cb = set(_split(b["high_risk_categories"]))
            rows.append(
                {
                    "family": family,
                    "file_sha_a": a["file_sha"],
                    "file_sha_b": b["file_sha"],
                    "similarity": round(sim, 3),
                    "ordered": ordered,
                    "only_in_a": ";".join(sorted(ca - cb)),
                    "only_in_b": ";".join(sorted(cb - ca)),
                    "differs": ca != cb,
                }
            )
    return pd.DataFrame(rows, columns=PAIR_COLUMNS)


def family_summary(
    scan: pd.DataFrame, pairs: pd.DataFrame, min_similarity: float = 0.5
) -> pd.DataFrame:
    sizes = _families(scan)
    sizes = sizes[sizes != ""].value_counts()
    multi = sizes[sizes >= 2]
    ordered = pairs["ordered"].astype(bool) if len(pairs) else pd.Series(dtype=bool)
    metrics = [
        ("families_with_2plus_variants", int(len(multi))),
        ("variants_in_those_families", int(multi.sum())),
        ("candidate_pairs", int(sum(n * (n - 1) // 2 for n in multi))),
        ("similarity_threshold", min_similarity),
        ("lineage_pairs", int(len(pairs))),
        ("families_with_lineage_pairs", int(pairs["family"].nunique()) if len(pairs) else 0),
        ("lineage_pairs_differing_high_risk", int(pairs["differs"].sum()) if len(pairs) else 0),
        ("ordered_lineage_pairs", int(ordered.sum())),
        (
            "ordered_pairs_newer_adds_high_risk",
            int((ordered & (pairs["only_in_b"] != "")).sum()) if len(pairs) else 0,
        ),
        (
            "ordered_pairs_newer_drops_high_risk",
            int((ordered & (pairs["only_in_a"] != "")).sum()) if len(pairs) else 0,
        ),
    ]
    return pd.DataFrame(metrics, columns=["metric", "value"])


def scan_siblings(siblings: pd.DataFrame, rules: list[Rule]) -> pd.DataFrame:
    """Scan bundled script files (text content only; never executed)."""
    cols = ["repo_full_name", "artifact_path", "entry_name", "rule_ids", "high_risk"]
    if siblings.empty:
        return pd.DataFrame(columns=cols)
    names = siblings["entry_name"].fillna("").astype(str).str.lower()
    scripts = siblings[names.str.endswith(SCRIPT_EXTENSIONS)]
    by_id = {r.id: r for r in rules}
    rows = []
    for rec in scripts.to_dict("records"):
        ids = scan_text(_text(rec.get("content")), rules)
        rows.append(
            {
                "repo_full_name": rec["repo_full_name"],
                "artifact_path": rec["artifact_path"],
                "entry_name": rec["entry_name"],
                "rule_ids": ";".join(ids),
                "high_risk": any(by_id[i].severity >= HIGH_RISK_SEVERITY for i in ids),
            }
        )
    return pd.DataFrame(rows, columns=cols)


def sibling_summary(sib_scan: pd.DataFrame) -> pd.DataFrame:
    if sib_scan.empty:
        metrics = [
            ("script_files_with_text", 0),
            ("script_files_with_any_signal", 0),
            ("script_files_with_high_risk_signal", 0),
            ("skills_with_scanned_scripts", 0),
            ("skills_with_high_risk_script", 0),
        ]
        return pd.DataFrame(metrics, columns=["metric", "value"])
    skill_key = sib_scan["repo_full_name"] + "\n" + sib_scan["artifact_path"]
    high = sib_scan["high_risk"].astype(bool)
    metrics = [
        ("script_files_with_text", int(len(sib_scan))),
        ("script_files_with_any_signal", int((sib_scan["rule_ids"] != "").sum())),
        ("script_files_with_high_risk_signal", int(high.sum())),
        ("skills_with_scanned_scripts", int(skill_key.nunique())),
        ("skills_with_high_risk_script", int(skill_key[high].nunique())),
    ]
    return pd.DataFrame(metrics, columns=["metric", "value"])


def validation_sample(
    scan: pd.DataFrame, n_per_category: int = 10, n_negative: int = 40, seed: int = 580
) -> pd.DataFrame:
    """Stratified sample for manual annotation: per high-risk category plus negatives."""
    parts = []
    cats = sorted({c for s in scan["high_risk_categories"] for c in _split(s)})
    for cat in cats:
        pool = scan[scan["high_risk_categories"].apply(lambda s, c=cat: c in _split(s))]
        take = pool.sample(n=min(n_per_category, len(pool)), random_state=seed)
        parts.append(take.assign(stratum=cat))
    negatives = scan[scan["rule_ids"] == ""]
    if len(negatives):
        take = negatives.sample(n=min(n_negative, len(negatives)), random_state=seed)
        parts.append(take.assign(stratum="NO_SIGNAL"))
    cols = ["file_sha", "name", "stratum", "rule_ids"]
    if not parts:
        return pd.DataFrame(columns=cols)
    return pd.concat(parts).drop_duplicates("file_sha")[cols].reset_index(drop=True)


# ---------------------------------------------------------------------------
# Orchestration
# ---------------------------------------------------------------------------


def run_pilot(
    db_path: Path,
    paths: Paths | None = None,
    rules_path: Path | str | None = None,
    limit: int | None = None,
    min_similarity: float = 0.5,
    seed: int = 580,
) -> list[Path]:
    """Run the pilot on a GitSkills SQLite file and write tables and a figure."""
    from . import explore
    from .load import query_gitskills

    paths = paths or get_paths()
    rules = load_rules(rules_path)
    lim = f" LIMIT {int(limit)}" if limit else ""
    reps = query_gitskills(
        "SELECT file_sha, name, content, first_commit_at FROM artifacts "
        "WHERE dedup_primary = 1 AND content IS NOT NULL ORDER BY file_sha" + lim,
        db_path,
    )
    occurrences = query_gitskills("SELECT file_sha, repo_full_name FROM artifacts", db_path)
    siblings = query_gitskills(
        "SELECT repo_full_name, artifact_path, entry_name, content FROM artifact_siblings "
        "WHERE entry_type = 'file' AND content IS NOT NULL",
        db_path,
    )

    scan = scan_contents(reps, rules)
    counts = copy_counts(occurrences)
    pairs = family_pairs(reps, scan, min_similarity=min_similarity)
    categories = category_prevalence(scan, counts, rules)

    tables = {
        "pilot_skill_risk_rules": rule_prevalence(scan, counts, rules),
        "pilot_skill_risk_categories": categories,
        "pilot_skill_risk_reach": reach_by_risk(scan, counts),
        "pilot_skill_risk_family_summary": family_summary(scan, pairs, min_similarity),
        "pilot_skill_risk_family_pairs": pairs,
        "pilot_skill_risk_siblings_summary": sibling_summary(scan_siblings(siblings, rules)),
    }
    produced = [explore.write_table(df, name, paths) for name, df in tables.items()]
    produced.append(
        explore.plot_bar(
            categories,
            "category",
            "content_share",
            "pilot_skill_risk_categories",
            title="GitSkills sample: share of distinct skills with each signal (unvalidated)",
            paths=paths,
        )
    )
    tmp = paths.RESULTS / "tmp"
    tmp.mkdir(parents=True, exist_ok=True)
    sample_path = tmp / "pilot_skill_risk_validation_sample.csv"
    validation_sample(scan, seed=seed).to_csv(sample_path, index=False)
    produced.append(sample_path)
    return produced
