"""Search notebook for requirements elicitation (assignment Phase B).

The notebook answers questions only from the pinned source pack that
``scripts/build_notebook_sources.py`` writes. It is extractive: an answer is the
passages that best match the question, quoted word for word with a locator
(source ID, file, section heading or page, line). It never writes text of its
own, so it cannot state something no source says. It can still return a passage
that does not answer the question, which is why the team verifies every answer
in ``elicitation/notebook-interview.md``.

A scope limits which tiers are searched, so dataset facts come from the
authoritative sources and nowhere else:

- ``dataset``: tier A, the MSR challenge page, preprints, Zenodo records, dataset
  cards, and GitHub mirrors
- ``gitskills`` and ``specmine``: the tier-A sources about that dataset only (the
  challenge page covers both), so a GitSkills question is not answered from the
  SpecMine data dictionary
- ``group``: tier G, Group 9's own documents
- ``process``: tiers G and P (a member's personal build method)
- ``all``: every tier

Ranking is Okapi BM25 over tokens. Identifiers such as ``content_sha_ok`` are
kept whole and also split into parts, so a question can match either form.
"""

from __future__ import annotations

import json
import math
import re
from collections import Counter
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path

import yaml

# scope -> (tiers searched, source IDs allowed; None means every ID in those tiers)
SCOPES: dict[str, tuple[frozenset[str], frozenset[str] | None]] = {
    "dataset": (frozenset({"authoritative"}), None),
    "gitskills": (frozenset({"authoritative"}), frozenset({"A1", "A2", "A4", "A6", "A9"})),
    "specmine": (frozenset({"authoritative"}), frozenset({"A1", "A3", "A5", "A7", "A8"})),
    "group": (frozenset({"group"}), None),
    "process": (frozenset({"group", "practitioner"}), None),
    "all": (frozenset({"authoritative", "group", "practitioner"}), None),
}
TIER_LETTER = {"authoritative": "A", "group": "G", "practitioner": "P"}

K1 = 1.5
B = 0.75
MAX_WORDS = 120  # passage size cap; longer blocks are split on line boundaries
MIN_WORDS = 12  # shorter blocks are merged into the next block in the same section
PER_SOURCE = 2  # at most this many passages from one file in a single answer
QUOTE_CHARS = 900
COVERAGE_ANSWERED = 0.5  # share of question terms the passages must contain for "match"

STOPWORDS = frozenset(
    """a about above after again all also am an and any are as at be because been before
    being between both but by can could did do does doing done each even every for from
    further had has have having how i if in into is it its itself just may me might more
    most must my no nor not now of off on once only or other our out over own per same
    shall should so some such than that the their them then there these they this those
    through to too under until up upon us very was we were what when where which while who
    whom why will with within without would you your exactly actually""".split()
)
_TOKEN = re.compile(r"[a-z0-9]+(?:_[a-z0-9]+)*")
_HEADING = re.compile(r"^(#{1,6})\s+(.*\S)\s*$")


def _stem(token: str) -> str:
    """Plural stripping only: enough to match "skills" with "skill" without a stemmer.
    Words ending in -ss, -us, or -is ("access", "malicious", "analysis") are left alone."""
    if len(token) <= 3 or not token.endswith("s") or token.endswith(("ss", "us", "is")):
        return token
    if len(token) > 4 and token.endswith("ies"):
        return token[:-3] + "y"
    if token.endswith(("ches", "shes", "xes", "zes")):
        return token[:-2]
    return token[:-1]


def tokenize(text: str) -> list[str]:
    """Lower-cased content tokens; ``a_b`` yields ``a_b``, ``a``, and ``b``."""
    out: list[str] = []
    for tok in _TOKEN.findall(text.lower()):
        parts = [tok] + (tok.split("_") if "_" in tok else [])
        out.extend(_stem(p) for p in parts if len(p) > 1 and p not in STOPWORDS)
    return out


@dataclass(frozen=True)
class Passage:
    """A searchable span of one source file."""

    source_id: str
    tier: str
    file: str
    section: str
    line: int
    text: str

    @property
    def locator(self) -> str:
        where = self.section or "(top of file)"
        return f"{self.source_id} · {self.file} · {where} · line {self.line}"


def _body_start(lines: list[str]) -> int:
    """Index of the first line after the pack header block (ended by a ``---`` line)."""
    for i, line in enumerate(lines[:20]):
        if line.strip() == "---" and lines[0].startswith("# "):
            return i + 1
    return 0


def split_passages(
    text: str, source_id: str, tier: str, file: str, max_words: int = MAX_WORDS
) -> list[Passage]:
    """Split Markdown into passages that carry their heading path and first line number.

    Blocks are separated by blank lines. Headings inside fenced code are not headings
    (YAML comments start with ``#``). Short blocks join the next block in the same
    section; long blocks are cut on line boundaries.
    """
    lines = text.splitlines()
    start = _body_start(lines)
    headings: dict[int, str] = {}
    in_fence = False
    blocks: list[tuple[str, int, list[str]]] = []  # (section, first line, lines)
    current: list[str] = []
    current_line = 0

    def section() -> str:
        return " > ".join(headings[k] for k in sorted(headings))

    def flush() -> None:
        nonlocal current
        if current:
            blocks.append((section(), current_line, current))
        current = []

    for number, line in enumerate(lines[start:], start=start + 1):
        stripped = line.strip()
        if stripped.startswith("```"):
            in_fence = not in_fence
        heading = None if in_fence else _HEADING.match(line)
        if heading:
            flush()
            level = len(heading.group(1))
            headings = {k: v for k, v in headings.items() if k < level}
            headings[level] = heading.group(2).strip("# ").strip()
            continue
        if not stripped:
            flush()
            continue
        if not current:
            current_line = number
        current.append(line)
    flush()

    passages: list[Passage] = []
    pending: tuple[str, int, list[str]] | None = None
    for sec, first, block in blocks:
        if pending and pending[0] == sec:
            first, block = pending[1], pending[2] + block
        elif pending:
            passages.extend(_cut(pending, source_id, tier, file, max_words))
        pending = None
        if len(" ".join(block).split()) < MIN_WORDS:
            pending = (sec, first, block)
            continue
        passages.extend(_cut((sec, first, block), source_id, tier, file, max_words))
    if pending:
        passages.extend(_cut(pending, source_id, tier, file, max_words))
    return [p for p in passages if tokenize(p.text)]


def _cut(
    block: tuple[str, int, list[str]], source_id: str, tier: str, file: str, max_words: int
) -> list[Passage]:
    sec, first, lines = block
    out: list[Passage] = []
    chunk: list[str] = []
    chunk_line = first
    words = 0
    for offset, line in enumerate(lines):
        n = len(line.split())
        if chunk and words + n > max_words:
            out.append(Passage(source_id, tier, file, sec, chunk_line, "\n".join(chunk)))
            chunk, words, chunk_line = [], 0, first + offset
        chunk.append(line)
        words += n
    if chunk:
        out.append(Passage(source_id, tier, file, sec, chunk_line, "\n".join(chunk)))
    return out


@dataclass
class Answer:
    """What the notebook returns for one question."""

    question: str
    scope: str
    hits: list[tuple[Passage, float]]
    terms: list[str]
    covered: list[str]
    qid: str = ""
    kind: str = ""
    follow_up_of: str = ""

    @property
    def missing(self) -> list[str]:
        return [t for t in self.terms if t not in self.covered]

    @property
    def coverage(self) -> float:
        return len(self.covered) / len(self.terms) if self.terms else 0.0

    @property
    def status(self) -> str:
        """``match``, ``weak match`` (under half the question's terms occur in the
        passages), or ``no match`` (no passage in scope shares a term with the question).

        This is a mechanical term-coverage label, not a judgement that the passages
        answer the question; the team decides that when it verifies the answer."""
        if not self.hits:
            return "no match"
        return "match" if self.coverage >= COVERAGE_ANSWERED else "weak match"

    @property
    def sources_cited(self) -> list[str]:
        seen: dict[str, None] = {}
        for p, _ in self.hits:
            seen.setdefault(p.source_id, None)
        return list(seen)

    def to_markdown(self) -> str:
        if self.qid:
            follow = f"; follow-up to {self.follow_up_of}" if self.follow_up_of else ""
            title = f"## {self.qid} ({self.kind}; scope: {self.scope}{follow})"
        else:
            title = f"## Question (scope: {self.scope})"
        lines = [
            title,
            "",
            f"**Question.** {self.question}",
            "",
            f"**Status.** {self.status}. Question terms found in the passages: "
            f"{len(self.covered)} of {len(self.terms)}.",
        ]
        if self.missing:
            lines.append(f"Terms no returned passage contains: {', '.join(self.missing)}.")
        lines += ["", f"**Sources cited.** {', '.join(self.sources_cited) or 'none'}", ""]
        if not self.hits:
            lines.append("_No passage in this scope matches the question._")
        for rank, (p, score) in enumerate(self.hits, 1):
            quote = p.text if len(p.text) <= QUOTE_CHARS else p.text[:QUOTE_CHARS] + " …"
            quoted = "\n".join("> " + ln if ln.strip() else ">" for ln in quote.splitlines())
            lines += [f"**[{rank}] {p.locator}** (BM25 {score:.1f})", "", quoted, ""]
        return "\n".join(lines).rstrip() + "\n"


@dataclass
class Notebook:
    """BM25 index over a source pack."""

    passages: list[Passage]
    manifest: dict = field(default_factory=dict)

    def __post_init__(self) -> None:
        self._docs = [Counter(tokenize(p.text + " " + p.section)) for p in self.passages]
        self._lengths = [sum(d.values()) for d in self._docs]
        df: Counter[str] = Counter()
        for doc in self._docs:
            df.update(doc.keys())
        n = len(self._docs) or 1
        self._idf = {t: math.log(1 + (n - f + 0.5) / (f + 0.5)) for t, f in df.items()}
        self._avg = (sum(self._lengths) / n) if self._lengths else 0.0

    @classmethod
    def from_pack(cls, pack_dir: Path | str) -> Notebook:
        """Index every Markdown source listed in the pack's ``SOURCES_MANIFEST.json``."""
        pack = Path(pack_dir)
        manifest_path = pack / "SOURCES_MANIFEST.json"
        if not manifest_path.is_file():
            raise FileNotFoundError(
                f"No SOURCES_MANIFEST.json in {pack}. Build the pack first: "
                "python scripts/build_notebook_sources.py"
            )
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        passages: list[Passage] = []
        for src in manifest["sources"]:
            path = pack / src["file"]
            if path.suffix == ".md" and path.is_file():
                text = path.read_text(encoding="utf-8")
                passages += split_passages(text, src["id"], src["tier"], src["file"])
        return cls(passages, manifest)

    def summary(self) -> dict[str, int]:
        """Passage counts per tier letter, plus the number of indexed files."""
        counts = Counter(TIER_LETTER[p.tier] for p in self.passages)
        return {"files": len({p.file for p in self.passages}), **dict(sorted(counts.items()))}

    def _score(self, terms: list[str], i: int) -> float:
        doc, length = self._docs[i], self._lengths[i]
        score = 0.0
        for t in terms:
            f = doc.get(t, 0)
            if f:
                norm = f + K1 * (1 - B + B * length / self._avg)
                score += self._idf[t] * f * (K1 + 1) / norm
        return score

    def ask(self, question: str, scope: str = "dataset", k: int = 3) -> Answer:
        """Return the ``k`` best passages in ``scope`` for ``question``."""
        if scope not in SCOPES:
            raise ValueError(f"scope must be one of {sorted(SCOPES)}, not {scope!r}")
        terms = list(dict.fromkeys(tokenize(question)))
        tiers, ids = SCOPES[scope]
        ranked = sorted(
            (
                (self._score(terms, i), i)
                for i, p in enumerate(self.passages)
                if p.tier in tiers and (ids is None or p.source_id in ids)
            ),
            key=lambda item: (-item[0], item[1]),
        )
        hits: list[tuple[Passage, float]] = []
        found: set[str] = set()
        per_file: Counter[str] = Counter()
        for score, i in ranked:
            if score <= 0 or len(hits) == k:
                break
            p = self.passages[i]
            if per_file[p.file] >= PER_SOURCE:
                continue
            per_file[p.file] += 1
            hits.append((p, score))
            found.update(self._docs[i])
        covered = [t for t in terms if t in found]
        return Answer(question, scope, hits, terms, covered)

    def interview(self, questions: list[dict], k: int = 3) -> list[Answer]:
        """Ask each prepared question word for word, in order, in its stated scope."""
        answers = []
        for q in questions:
            ans = self.ask(q["question"], q.get("scope", "dataset"), k)
            ans.qid, ans.kind = q["id"], q.get("kind", "")
            ans.follow_up_of = q.get("follow_up_of", "")
            answers.append(ans)
        return answers


def load_questions(path: Path | str) -> list[dict]:
    """Prepared questions from YAML: a list under ``questions`` with id, kind, scope,
    question, informs, and check_against."""
    data = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    questions = data["questions"]
    ids = [q["id"] for q in questions]
    if len(ids) != len(set(ids)):
        raise ValueError("duplicate question ids")
    for q in questions:
        if q.get("scope", "dataset") not in SCOPES:
            raise ValueError(f"{q['id']}: unknown scope {q.get('scope')!r}")
        parent = q.get("follow_up_of")
        if parent and parent not in ids[: ids.index(q["id"])]:
            raise ValueError(f"{q['id']}: follow-up of {parent!r}, which is not asked before it")
    return questions


def render_transcript(answers: list[Answer], notebook: Notebook, k: int) -> str:
    """The interview transcript: provenance header, then each answer verbatim."""
    m = notebook.manifest
    counts = notebook.summary()
    tiers = ", ".join(f"{t} {n} passages" for t, n in counts.items() if t != "files")
    lines = [
        "# Notebook interview transcript",
        "",
        "Generated by `python -m msr_pipeline elicit`. Do not edit by hand: the team's "
        "interpretation and verification of each answer are in "
        "`elicitation/notebook-interview.md`.",
        "",
        "| Item | Value |",
        "|---|---|",
        f"| Generated | {datetime.now(UTC).strftime('%Y-%m-%d %H:%M UTC')} |",
        f"| Source pack | built {m.get('generated_at', '?')}; repository commit "
        f"`{str(m.get('repo_commit', '?'))[:12]}`; {counts['files']} files indexed; {tiers} |",
        f"| Tier P included | {'yes' if m.get('practice_included') else 'no'} |",
        f"| Method | BM25 (k1 {K1}, b {B}); passages of at most {MAX_WORDS} words; top {k} "
        f"per question, at most {PER_SOURCE} per file |",
        f'| Status | "match" means at least {COVERAGE_ANSWERED:.0%} of the question\'s terms '
        "occur in the returned passages. It does not mean the passages answer the question; "
        "the team decides that in the interview record |",
        "",
    ]
    for ans in answers:
        lines += [ans.to_markdown(), "---", ""]
    return "\n".join(lines)
