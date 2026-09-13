"""Ranked-ballot tallying for the topic vote.

Ballots are YAML files with a ranking of proposal issue numbers (best first) and
per-criterion scores. The winner is chosen by instant runoff on the rankings; ties are
broken by the weighted-criteria score, then by Borda count. All functions are pure and
covered by tests/test_voting.py.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import yaml

DEFAULT_WEIGHTS: dict[str, float] = {
    "feasibility": 0.30,
    "data_fit": 0.20,
    "rubric_fit": 0.20,
    "interest": 0.15,
    "low_risk": 0.15,
}
SCORE_MIN = 1
SCORE_MAX = 5


class BallotError(ValueError):
    """Raised when a ballot file cannot be parsed into a Ballot."""


@dataclass
class Ballot:
    voter: str
    ranking: list[int]
    scores: dict[int, dict[str, float]] = field(default_factory=dict)
    date: str | None = None
    comment: str = ""
    source: str = ""


@dataclass
class IRVResult:
    winner: int | None
    rounds: list[dict[int, int]]
    eliminated: list[int]
    tied: list[int]
    tiebreak_used: bool = False


@dataclass
class TallyResult:
    n_ballots: int
    candidates: list[int]
    winner: int | None
    decided_by: str
    irv: IRVResult
    borda: dict[int, float]
    weighted: dict[int, float | None]
    problems: list[str]


def parse_ballot(data: dict[str, Any], source: str = "") -> Ballot:
    """Validate raw YAML data and build a Ballot. Raises BallotError on structural errors."""
    if not isinstance(data, dict):
        raise BallotError(f"{source}: ballot must be a mapping")
    voter = str(data.get("voter", "")).strip().lstrip("@").lower()
    if not voter or voter == "your-github-handle":
        raise BallotError(f"{source}: 'voter' must be your GitHub handle")
    ranking_raw = data.get("ranking")
    if not isinstance(ranking_raw, list) or not ranking_raw:
        raise BallotError(f"{source}: 'ranking' must be a non-empty list of issue numbers")
    ranking: list[int] = []
    for item in ranking_raw:
        if isinstance(item, bool) or not isinstance(item, int):
            raise BallotError(f"{source}: ranking entry {item!r} is not an integer issue number")
        ranking.append(item)
    scores_raw = data.get("scores") or {}
    if not isinstance(scores_raw, dict):
        raise BallotError(f"{source}: 'scores' must be a mapping of issue number to criteria")
    scores: dict[int, dict[str, float]] = {}
    for key, crit in scores_raw.items():
        try:
            cand = int(key)
        except (TypeError, ValueError) as exc:
            raise BallotError(f"{source}: score key {key!r} is not an issue number") from exc
        if not isinstance(crit, dict):
            raise BallotError(f"{source}: scores for {cand} must be a mapping")
        scores[cand] = {str(k): float(v) for k, v in crit.items()}
    date = data.get("date")
    return Ballot(
        voter=voter,
        ranking=ranking,
        scores=scores,
        date=str(date) if date is not None else None,
        comment=str(data.get("comment") or ""),
        source=source,
    )


def load_ballots(directory: str | Path) -> tuple[list[Ballot], list[str]]:
    """Load every *.yml / *.yaml ballot in a directory. Returns (ballots, problems)."""
    directory = Path(directory)
    ballots: list[Ballot] = []
    problems: list[str] = []
    if not directory.exists():
        return ballots, [f"ballot directory not found: {directory}"]
    for path in sorted(directory.glob("*.y*ml")):
        if path.name.upper().startswith("TEMPLATE"):
            continue
        try:
            data = yaml.safe_load(path.read_text(encoding="utf-8"))
            ballots.append(parse_ballot(data, source=path.name))
        except (yaml.YAMLError, BallotError) as exc:
            problems.append(str(exc))
    return ballots, problems


def validate_ballots(
    ballots: list[Ballot],
    weights: dict[str, float] | None = None,
    candidates: set[int] | None = None,
) -> list[str]:
    """Return a list of human-readable problems. An empty list means all ballots are valid."""
    weights = weights or DEFAULT_WEIGHTS
    problems: list[str] = []
    seen_voters: set[str] = set()
    for b in ballots:
        src = b.source or b.voter
        if b.voter in seen_voters:
            problems.append(f"{src}: duplicate ballot for voter '{b.voter}'")
        seen_voters.add(b.voter)
        if len(set(b.ranking)) != len(b.ranking):
            problems.append(f"{src}: ranking contains a repeated proposal")
        if candidates is not None:
            unknown = [c for c in b.ranking if c not in candidates]
            if unknown:
                problems.append(f"{src}: ranking references unknown proposals {unknown}")
        for cand in b.ranking:
            if cand not in b.scores:
                problems.append(f"{src}: no scores given for ranked proposal {cand}")
        for cand, crit in b.scores.items():
            if cand not in b.ranking:
                problems.append(f"{src}: scores given for unranked proposal {cand}")
            for name, value in crit.items():
                if name not in weights:
                    problems.append(f"{src}: unknown criterion '{name}' for proposal {cand}")
                elif not (SCORE_MIN <= value <= SCORE_MAX):
                    problems.append(
                        f"{src}: score {name}={value} for proposal {cand} is outside "
                        f"{SCORE_MIN}..{SCORE_MAX}"
                    )
            missing = [w for w in weights if w not in crit]
            if missing:
                problems.append(f"{src}: proposal {cand} is missing criteria {missing}")
    return problems


def candidates_from(ballots: list[Ballot]) -> list[int]:
    return sorted({c for b in ballots for c in b.ranking})


def borda(ballots: list[Ballot], candidates: list[int]) -> dict[int, float]:
    """Borda count: a candidate ranked at position i (0-based) on a ballot gets n - i points."""
    n = len(candidates)
    points = {c: 0.0 for c in candidates}
    for b in ballots:
        for i, cand in enumerate(b.ranking):
            if cand in points:
                points[cand] += n - i
    return points


def weighted_scores(
    ballots: list[Ballot], weights: dict[str, float] | None = None
) -> dict[int, float | None]:
    """Mean weighted-criteria score per candidate on the 1..5 scale.

    A ballot contributes to a candidate only if it scored that candidate. Missing criteria
    on a ballot are ignored and the remaining weights are renormalised.
    """
    weights = weights or DEFAULT_WEIGHTS
    totals: dict[int, list[float]] = {}
    for b in ballots:
        for cand, crit in b.scores.items():
            used = {k: w for k, w in weights.items() if k in crit}
            wsum = sum(used.values())
            if wsum <= 0:
                continue
            score = sum(crit[k] * w for k, w in used.items()) / wsum
            totals.setdefault(cand, []).append(score)
    return {c: (sum(v) / len(v) if v else None) for c, v in totals.items()}


def instant_runoff(
    ballots: list[Ballot],
    candidates: list[int],
    tiebreak: dict[int, float] | None = None,
) -> IRVResult:
    """Instant-runoff vote.

    Each round counts first preferences among remaining candidates. A candidate with more
    than half of the active ballots wins. Otherwise the candidate with the fewest first
    preferences is eliminated; ties for last place are broken by `tiebreak` (lower value
    eliminated first). If a tie for last cannot be broken and eliminating all tied
    candidates would leave nobody, the result is a tie.
    """
    remaining = list(candidates)
    rounds: list[dict[int, int]] = []
    eliminated: list[int] = []
    tiebreak = tiebreak or {}
    used_tiebreak = False
    while remaining:
        counts = {c: 0 for c in remaining}
        active = 0
        for b in ballots:
            for cand in b.ranking:
                if cand in counts:
                    counts[cand] += 1
                    active += 1
                    break
        rounds.append(dict(counts))
        if active == 0:
            return IRVResult(None, rounds, eliminated, sorted(remaining), used_tiebreak)
        leader = max(remaining, key=lambda c: counts[c])
        if counts[leader] * 2 > active:
            return IRVResult(leader, rounds, eliminated, [], used_tiebreak)
        if len(remaining) == 1:
            return IRVResult(remaining[0], rounds, eliminated, [], used_tiebreak)
        lowest = min(counts[c] for c in remaining)
        losers = [c for c in remaining if counts[c] == lowest]
        if len(losers) > 1:
            keyed = sorted(losers, key=lambda c: (tiebreak.get(c, float("-inf")), -c))
            worst_key = tiebreak.get(keyed[0], float("-inf"))
            still_tied = [c for c in losers if tiebreak.get(c, float("-inf")) == worst_key]
            if len(still_tied) == len(remaining):
                return IRVResult(None, rounds, eliminated, sorted(remaining), used_tiebreak)
            losers = [keyed[0]] if len(still_tied) == 1 else still_tied
            if len(losers) == len(remaining):
                return IRVResult(None, rounds, eliminated, sorted(remaining), used_tiebreak)
            used_tiebreak = True
        for loser in losers:
            remaining.remove(loser)
            eliminated.append(loser)
    return IRVResult(None, rounds, eliminated, [], used_tiebreak)


def tally(
    ballots: list[Ballot],
    weights: dict[str, float] | None = None,
    candidates: list[int] | None = None,
) -> TallyResult:
    """Full tally: validation, IRV, Borda, weighted scores, and tie-breaking."""
    weights = weights or DEFAULT_WEIGHTS
    cands = candidates if candidates is not None else candidates_from(ballots)
    problems = validate_ballots(ballots, weights, set(cands) if candidates else None)
    borda_pts = borda(ballots, cands)
    weighted = weighted_scores(ballots, weights)
    weighted_key = {c: (weighted.get(c) or 0.0) + borda_pts[c] / 1e6 for c in cands}
    irv = instant_runoff(ballots, cands, tiebreak=weighted_key)
    winner = irv.winner
    decided_by = "instant runoff"
    if winner is not None and irv.tiebreak_used:
        decided_by = "instant runoff with weighted-score tie-break in elimination"
    if winner is None and irv.tied:
        best_w = max(irv.tied, key=lambda c: weighted.get(c) or 0.0)
        top = [c for c in irv.tied if (weighted.get(c) or 0.0) == (weighted.get(best_w) or 0.0)]
        if len(top) == 1:
            winner, decided_by = top[0], "weighted score tie-break"
        else:
            best_b = max(top, key=lambda c: borda_pts[c])
            top_b = [c for c in top if borda_pts[c] == borda_pts[best_b]]
            if len(top_b) == 1:
                winner, decided_by = top_b[0], "Borda tie-break"
            else:
                decided_by = f"unresolved tie between {sorted(top_b)}"
    elif winner is None:
        decided_by = "no valid ballots"
    return TallyResult(
        n_ballots=len(ballots),
        candidates=cands,
        winner=winner,
        decided_by=decided_by,
        irv=irv,
        borda=borda_pts,
        weighted=weighted,
        problems=problems,
    )


def render_markdown(
    result: TallyResult,
    titles: dict[int, str] | None = None,
    generated_at: datetime | None = None,
) -> str:
    """Render a TallyResult as the RESULTS.md document."""
    titles = titles or {}
    ts = (generated_at or datetime.now(UTC)).strftime("%Y-%m-%d %H:%M UTC")

    def name(c: int) -> str:
        t = titles.get(c)
        return f"#{c} {t}" if t else f"#{c}"

    lines = ["# Topic vote results", "", f"Generated {ts} by `scripts/tally_votes.py`.", ""]
    if result.winner is not None:
        lines += [f"**Winner: {name(result.winner)}** (decided by {result.decided_by}).", ""]
    else:
        lines += [f"**No winner yet** ({result.decided_by}).", ""]
    lines += [f"Ballots counted: {result.n_ballots}. Candidates: {len(result.candidates)}.", ""]
    if result.problems:
        lines += ["## Problems", ""] + [f"- {p}" for p in result.problems] + [""]
    lines += ["## Standings", "", "| Proposal | Weighted score (1-5) | Borda | Final IRV round |"]
    lines += ["|---|---|---|---|"]
    last_round = result.irv.rounds[-1] if result.irv.rounds else {}
    order = sorted(
        result.candidates,
        key=lambda c: (-(result.weighted.get(c) or 0.0), -result.borda.get(c, 0.0)),
    )
    for c in order:
        w = result.weighted.get(c)
        w_txt = f"{w:.2f}" if w is not None else "n/a"
        lines.append(
            f"| {name(c)} | {w_txt} | {result.borda.get(c, 0):.0f} | {last_round.get(c, '-')} |"
        )
    lines += ["", "## Instant-runoff rounds", ""]
    for i, rnd in enumerate(result.irv.rounds, start=1):
        parts = ", ".join(f"{name(c)}: {v}" for c, v in sorted(rnd.items(), key=lambda kv: -kv[1]))
        lines.append(f"- Round {i}: {parts}")
    if result.irv.eliminated:
        lines.append("- Eliminated in order: " + ", ".join(name(c) for c in result.irv.eliminated))
    lines += ["", "## Method", ""]
    lines += [
        "Instant runoff on rankings; ties broken by the weighted-criteria score, then Borda count. "
        "Weights are defined in `project.yml`. See `docs/proposals/README.md`.",
        "",
    ]
    return "\n".join(lines)
