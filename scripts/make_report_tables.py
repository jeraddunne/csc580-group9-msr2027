import csv
import re
from decimal import ROUND_HALF_UP, Decimal
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "report" / "draft.md"

CAPABILITIES = {
    "TOOL_GRANT": ("Unscoped shell tool grant", "R-TGR-001"),
    "DESTRUCTIVE": ("Recursive forced delete or history rewrite", "R-DST-001"),
    "PRIVILEGE": ("`sudo`", "R-PRV-001"),
    "OVERSIGHT_BYPASS": ("Oversight bypass wording", "R-OVR-001"),
    "DYNAMIC_EXEC": ("Dynamic code execution", "R-EXE-001"),
    "PERSISTENCE": ("Persistence locations", "R-PER-001"),
    "REMOTE_CODE": ("Download and execute", "R-RCE-001, R-RCE-002"),
    "CREDENTIALS": ("Credential file paths", "R-CRD-001"),
    "OBFUSCATION": ("Obfuscated payload decoding", "R-OBF-001"),
    "NETWORK": ("Hard-coded IP endpoint", "R-NET-002"),
    "EXFIL_ENDPOINT": ("Request-capture or paste endpoint", "R-EXF-001"),
}


def load_rows(filename, key):
    with (ROOT / "results" / filename).open(encoding="utf-8", newline="") as source:
        return {row[key]: row for row in csv.DictReader(source)}


def count(value):
    return f"{int(value):,}"


def rounded(value, digits):
    return str(Decimal(value).quantize(Decimal(1).scaleb(-digits), rounding=ROUND_HALF_UP))


def population_rows():
    rows = load_rows("population_flow.csv", "step")
    labels = {
        "all_occurrences": "All sample occurrences",
        "excluded_symlink_stubs": "Excluded: symlink stubs",
        "main_population": "Main population",
        "frontmatter_valid_subset": "Sensitivity subset: valid front matter",
    }
    if rows["all_occurrences"]["occurrences"] == rows["with_content"]["occurrences"]:
        labels["all_occurrences"] += ", all with fetched text"
    for step, label in labels.items():
        row = rows[step]
        yield label, count(row["distinct_contents"]), count(row["occurrences"])


def precision_interval(row, kind):
    value = rounded(row[f"{kind}_precision"], 2)
    low = rounded(row[f"{kind}_ci_low"], 2)
    high = rounded(row[f"{kind}_ci_high"], 2)
    return f"{value} ({low} to {high})"


def precision_rows():
    rows = load_rows("validation_precision_by_category.csv", "category")
    ordered = sorted(rows.values(), key=lambda row: -float(row["strict_precision"]))
    for row in ordered:
        label, _ = CAPABILITIES[row["category"]]
        counts = " / ".join(
            count(row[key]) for key in ("risky", "benign_context", "not_present")
        )
        yield (
            label,
            count(row["n"]),
            counts,
            precision_interval(row, "strict"),
            precision_interval(row, "capability"),
        )


def prevalence_rows():
    rules = load_rows("rq1_prevalence_by_rule.csv", "rule_id")
    categories = load_rows("rq1_prevalence_by_category.csv", "category")
    population = load_rows("population_flow.csv", "step")
    total = Decimal(population["main_population"]["occurrences"])

    for category, (label, rule_ids) in CAPABILITIES.items():
        if category == "REMOTE_CODE":
            row = categories[category]
            prefix = "high_risk_"
        else:
            row = rules[rule_ids]
            prefix = ""

        share = Decimal(row["high_risk_share" if prefix else "content_share"]) * 100
        low = Decimal(row["high_risk_ci_low" if prefix else "content_ci_low"]) * 100
        high = Decimal(row["high_risk_ci_high" if prefix else "content_ci_high"]) * 100
        copies = Decimal(row[f"{prefix}occurrences"]) * 100 / total
        digits = 2 if 0 < copies < Decimal("0.1") else 1
        yield (
            label,
            rule_ids,
            count(row[f"{prefix}contents"]),
            f"{rounded(share, 1)}% ({rounded(low, 1)} to {rounded(high, 1)})",
            count(row[f"{prefix}occurrences"]),
            f"{rounded(copies, digits)}%",
        )


def replace_rows(report, number, rows):
    pattern = rf"(^Table {number}\. [^\n]+\n\n\|[^\n]+\n\|[^\n]+\n)(?:\|[^\n]*\n)+"
    body = "".join("| " + " | ".join(row) + " |\n" for row in rows)
    report, matches = re.subn(
        pattern, lambda match: match[1] + body, report, flags=re.MULTILINE
    )
    if matches != 1:
        raise SystemExit(f"Expected one Markdown table for Table {number}, found {matches}.")
    return report


def main():
    original = REPORT.read_text(encoding="utf-8")
    report = replace_rows(original, 1, population_rows())
    report = replace_rows(report, 2, precision_rows())
    report = replace_rows(report, 3, prevalence_rows())
    if report != original:
        REPORT.write_text(report, encoding="utf-8")
        print(f"Updated {REPORT.relative_to(ROOT)}")
    else:
        print("Report tables already match the source CSVs.")


if __name__ == "__main__":
    main()