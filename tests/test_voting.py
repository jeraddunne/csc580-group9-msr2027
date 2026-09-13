"""Tests for msr_pipeline.voting (offline, synthetic ballots)."""

from __future__ import annotations

from pathlib import Path

import pytest

from msr_pipeline.voting import (
    DEFAULT_WEIGHTS,
    Ballot,
    BallotError,
    borda,
    instant_runoff,
    load_ballots,
    parse_ballot,
    render_markdown,
    tally,
    validate_ballots,
    weighted_scores,
)


def full_scores(*cands: int, value: float = 4.0) -> dict[int, dict[str, float]]:
    return {c: {k: value for k in DEFAULT_WEIGHTS} for c in cands}


def ballot(voter: str, ranking: list[int], scores=None) -> Ballot:
    return Ballot(voter=voter, ranking=ranking, scores=scores or full_scores(*ranking))


def test_irv_first_round_majority():
    ballots = [ballot("a", [1, 2]), ballot("b", [1, 3]), ballot("c", [2, 1])]
    res = instant_runoff(ballots, [1, 2, 3])
    assert res.winner == 1
    assert len(res.rounds) == 1


def test_irv_elimination_transfers_votes():
    # 1 has 2 first prefs, 2 has 2, 3 has 1; 3 eliminated, its vote transfers to 2.
    ballots = [
        ballot("a", [1, 2]),
        ballot("b", [1, 2]),
        ballot("c", [2, 1]),
        ballot("d", [2, 1]),
        ballot("e", [3, 2]),
    ]
    res = instant_runoff(ballots, [1, 2, 3])
    assert res.eliminated == [3]
    assert res.winner == 2
    assert res.rounds[-1] == {1: 2, 2: 3}


def test_irv_exhausted_ballots_do_not_count_as_active():
    ballots = [ballot("a", [1]), ballot("b", [2]), ballot("c", [3, 1])]
    res = instant_runoff(ballots, [1, 2, 3], tiebreak={1: 3.0, 2: 2.0, 3: 1.0})
    # 3 has lowest tiebreak among the three-way tie and is eliminated; its vote goes to 1.
    assert res.eliminated[0] == 3
    assert res.winner == 1


def test_irv_unresolvable_tie_reports_tied():
    ballots = [ballot("a", [1]), ballot("b", [2])]
    res = instant_runoff(ballots, [1, 2])
    assert res.winner is None
    assert res.tied == [1, 2]


def test_borda_points():
    ballots = [ballot("a", [1, 2, 3]), ballot("b", [2, 1])]
    pts = borda(ballots, [1, 2, 3])
    assert pts == {1: 3 + 2, 2: 2 + 3, 3: 1}


def test_weighted_scores_uses_weights_and_averages():
    scores_a = {1: {"feasibility": 5, "data_fit": 1, "rubric_fit": 1, "interest": 1, "low_risk": 1}}
    scores_b = {1: {"feasibility": 1, "data_fit": 1, "rubric_fit": 1, "interest": 1, "low_risk": 1}}
    ballots = [ballot("a", [1], scores_a), ballot("b", [1], scores_b)]
    ws = weighted_scores(ballots)
    # Ballot a: 0.3*5 + 0.7*1 = 2.2 ; ballot b: 1.0 ; mean 1.6
    assert ws[1] == pytest.approx(1.6)


def test_weighted_scores_renormalises_missing_criteria():
    ballots = [ballot("a", [1], {1: {"feasibility": 4, "interest": 2}})]
    ws = weighted_scores(ballots)
    expected = (4 * 0.30 + 2 * 0.15) / 0.45
    assert ws[1] == pytest.approx(expected)


def test_tally_breaks_irv_tie_with_weighted_score():
    ballots = [
        ballot("a", [1], {1: {k: 5 for k in DEFAULT_WEIGHTS}}),
        ballot("b", [2], {2: {k: 3 for k in DEFAULT_WEIGHTS}}),
    ]
    res = tally(ballots)
    assert res.winner == 1
    assert "tie-break" in res.decided_by


def test_tally_reports_unresolved_tie():
    ballots = [ballot("a", [1]), ballot("b", [2])]
    res = tally(ballots)
    assert res.winner is None
    assert "unresolved tie" in res.decided_by


def test_validate_detects_problems():
    b = Ballot(
        voter="x",
        ranking=[1, 1, 9],
        scores={1: {"feasibility": 7, "bogus": 1}, 5: full_scores(5)[5]},
    )
    problems = validate_ballots([b, b], candidates={1, 2})
    text = "\n".join(problems)
    assert "duplicate ballot" in text
    assert "repeated proposal" in text
    assert "unknown proposals [9]" in text
    assert "outside 1..5" in text
    assert "unknown criterion 'bogus'" in text
    assert "unranked proposal 5" in text
    assert "missing criteria" in text


def test_parse_ballot_rejects_template_and_bad_types():
    with pytest.raises(BallotError):
        parse_ballot({"voter": "your-github-handle", "ranking": [1]})
    with pytest.raises(BallotError):
        parse_ballot({"voter": "x", "ranking": ["one"]})
    with pytest.raises(BallotError):
        parse_ballot({"voter": "x", "ranking": []})
    b = parse_ballot({"voter": "@Alice", "ranking": [3], "scores": {"3": {"feasibility": 4}}})
    assert b.voter == "alice"
    assert b.scores == {3: {"feasibility": 4.0}}


def test_load_ballots_skips_template_and_reports_bad_files(tmp_path: Path):
    (tmp_path / "TEMPLATE-ballot.yml").write_text("voter: your-github-handle\nranking: [1]\n")
    (tmp_path / "alice.yml").write_text(
        "voter: alice\nranking: [4, 2]\nscores:\n"
        "  4: {feasibility: 5, data_fit: 4, rubric_fit: 4, interest: 4, low_risk: 4}\n"
        "  2: {feasibility: 3, data_fit: 3, rubric_fit: 3, interest: 3, low_risk: 3}\n"
    )
    (tmp_path / "broken.yml").write_text("voter: bob\nranking: nope\n")
    ballots, problems = load_ballots(tmp_path)
    assert [b.voter for b in ballots] == ["alice"]
    assert len(problems) == 1 and "broken.yml" in problems[0]


def test_render_markdown_mentions_winner_and_rounds():
    ballots = [ballot("a", [1, 2]), ballot("b", [1, 2]), ballot("c", [2, 1])]
    res = tally(ballots)
    md = render_markdown(res, titles={1: "Skill reuse", 2: "Spec abandonment"})
    assert "Winner: #1 Skill reuse" in md
    assert "Round 1" in md
    assert "| #2 Spec abandonment |" in md
