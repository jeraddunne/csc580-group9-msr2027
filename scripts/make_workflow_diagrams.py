#!/usr/bin/env python
"""Draw the human-in-the-loop review workflow diagrams (UML use case and activity).

Writes two SVG files to docs/research/figures/. Positions are placed by hand so the
diagrams stay readable; change the text or coordinates here and re-run. Standard
library only. Nothing from the dataset is read.

Usage:
    python scripts/make_workflow_diagrams.py
"""

from __future__ import annotations

from html import escape
from pathlib import Path

OUT = Path(__file__).resolve().parents[1] / "docs" / "research" / "figures"
FONT = "font-family='Helvetica, Arial, sans-serif'"
INK = "#1f2328"
MUTED = "#57606a"


def svg(width: int, height: int, body: list[str], title: str) -> str:
    return "\n".join(
        [
            f"<svg xmlns='http://www.w3.org/2000/svg' width='{width}' height='{height}' "
            f"viewBox='0 0 {width} {height}' role='img' aria-label='{escape(title)}'>",
            f"<title>{escape(title)}</title>",
            "<defs>",
            "<marker id='open' viewBox='0 0 10 10' refX='9' refY='5' "
            "markerWidth='9' markerHeight='9' orient='auto'>"
            f"<path d='M0,0 L10,5 L0,10' fill='none' stroke='{INK}' stroke-width='1.4'/></marker>",
            "<marker id='solid' viewBox='0 0 10 10' refX='9' refY='5' "
            "markerWidth='8' markerHeight='8' orient='auto'>"
            f"<path d='M0,0 L10,5 L0,10 z' fill='{INK}'/></marker>",
            "</defs>",
            f"<rect width='{width}' height='{height}' fill='#ffffff'/>",
            *body,
            "</svg>",
            "",
        ]
    )


def text(
    x: float,
    y: float,
    lines: list[str] | str,
    size: int = 13,
    anchor: str = "middle",
    weight: str = "normal",
    color: str = INK,
    italic: bool = False,
) -> str:
    lines = [lines] if isinstance(lines, str) else lines
    lead = size * 1.25
    top = y - (len(lines) - 1) * lead / 2
    style = " font-style='italic'" if italic else ""
    spans = "".join(
        f"<tspan x='{x}' y='{top + i * lead:.1f}'>{escape(line)}</tspan>"
        for i, line in enumerate(lines)
    )
    return (
        f"<text {FONT} font-size='{size}' text-anchor='{anchor}' dominant-baseline='middle' "
        f"font-weight='{weight}' fill='{color}'{style}>{spans}</text>"
    )


def line(x1, y1, x2, y2, dashed=False, arrow: str | None = None, width=1.3) -> str:
    dash = " stroke-dasharray='6 4'" if dashed else ""
    end = f" marker-end='url(#{arrow})'" if arrow else ""
    return (
        f"<line x1='{x1}' y1='{y1}' x2='{x2}' y2='{y2}' "
        f"stroke='{INK}' stroke-width='{width}'{dash}{end}/>"
    )


def path(points: list[tuple[float, float]], arrow: str | None = "solid") -> str:
    d = "M" + " L".join(f"{x},{y}" for x, y in points)
    end = f" marker-end='url(#{arrow})'" if arrow else ""
    return f"<path d='{d}' fill='none' stroke='{INK}' stroke-width='1.3'{end}/>"


# ---------------------------------------------------------------- use case diagram


def actor(x: float, y: float, name: list[str] | str) -> list[str]:
    s = f"stroke='{INK}' stroke-width='1.5' fill='none'"
    return [
        f"<circle cx='{x}' cy='{y - 30}' r='10' stroke='{INK}' stroke-width='1.5' fill='#ffffff'/>",
        f"<line x1='{x}' y1='{y - 20}' x2='{x}' y2='{y + 8}' {s}/>",
        f"<line x1='{x - 16}' y1='{y - 10}' x2='{x + 16}' y2='{y - 10}' {s}/>",
        f"<line x1='{x}' y1='{y + 8}' x2='{x - 13}' y2='{y + 28}' {s}/>",
        f"<line x1='{x}' y1='{y + 8}' x2='{x + 13}' y2='{y + 28}' {s}/>",
        text(x, y + 46, name),
    ]


def usecase(x: float, y: float, label: list[str], rx: int = 118, ry: int = 32) -> str:
    return (
        f"<ellipse cx='{x}' cy='{y}' rx='{rx}' ry='{ry}' fill='#f6f8fa' "
        f"stroke='{INK}' stroke-width='1.3'/>" + text(x, y, label)
    )


def use_case_diagram() -> str:
    W, H = 1000, 640
    uc = {
        "U1": (340, 120, ["Propose or enable", "a skill"]),
        "U2": (630, 120, ["Scan the skill", "(static, nothing runs)"]),
        "U3": (340, 240, ["Read the scan report"]),
        "U5": (630, 280, ["Approve, block, or", "request a change"]),
        "U6": (340, 400, ["Revise the skill"]),
        "U4": (630, 420, ["Triage each finding", "(RISKY / BENIGN_CONTEXT /", "NOT_PRESENT)"]),
        "U7": (630, 550, ["Propose a rule change"]),
    }
    rx = {"U4": 140}
    b = [
        f"<rect x='200' y='50' width='590' height='560' rx='6' fill='none' "
        f"stroke='{INK}' stroke-width='1.5'/>",
        text(
            495, 72, "Skill risk review: P-01 scanner with a human reviewer", size=14, weight="bold"
        ),
    ]
    # associations (actor to use case), drawn first so ellipses sit on top
    assoc = [
        ((105, 150), "U1"),
        ((105, 150), "U3"),
        ((105, 410), "U6"),
        ((895, 120), "U2"),
        ((895, 340), "U5"),
        ((895, 340), "U4"),
        ((895, 560), "U7"),
    ]
    for (ax, ay), u in assoc:
        ux, uy, _ = uc[u]
        r = rx.get(u, 118)
        tx = ux - r if ax < ux else ux + r
        b.append(line(ax, ay, tx, uy))
    for k, (x, y, lab) in uc.items():
        b.append(usecase(x, y, lab, rx=rx.get(k, 118)))
    # «include»: proposing a skill always runs a scan
    b.append(line(458, 120, 510, 120, dashed=True, arrow="open"))
    b.append(text(484, 104, "«include»", size=12, color=MUTED))
    # «extend»: revising extends the decision when a change is requested
    b.append(line(445, 385, 520, 300, dashed=True, arrow="open"))
    b.append(text(478, 318, "«extend»", size=12, color=MUTED, anchor="end"))
    b.append(text(478, 334, "[change requested]", size=11, color=MUTED, anchor="end"))
    # «extend»: a rule-change proposal extends triage when a false positive is found
    b.append(line(630, 518, 630, 454, dashed=True, arrow="open"))
    b.append(
        text(640, 482, "«extend» [false positive found]", size=11, color=MUTED, anchor="start")
    )
    b += actor(80, 150, "Developer")
    b += actor(80, 410, "Skill author")
    b += actor(920, 120, ["CI pipeline", "«system»"])
    b += actor(920, 340, ["Security", "reviewer"])
    b += actor(920, 560, ["Rule", "maintainer"])
    return svg(W, H, b, "Use case diagram: human-in-the-loop skill risk review")


# ---------------------------------------------------------------- activity diagram

# (name, width). The reviewer lane is wider: its right column holds the block-or-revise branch.
LANES = [
    ("Developer", 200),
    ("Scanner (automated)", 210),
    ("Security reviewer", 340),
    ("Skill author", 190),
    ("Rule maintainer", 210),
]
LEFT = 10


def lane_left(i: int) -> float:
    return LEFT + sum(w for _, w in LANES[:i])


def action(x: float, y: float, label: list[str], w: int = 190, h: int = 54) -> str:
    return (
        f"<rect x='{x - w / 2}' y='{y - h / 2}' width='{w}' height='{h}' rx='14' fill='#f6f8fa' "
        f"stroke='{INK}' stroke-width='1.3'/>" + text(x, y, label, size=12)
    )


def send_signal(x: float, y: float, label: list[str], w: int = 190, h: int = 54) -> str:
    """UML send signal action: a box with a pointed right side."""
    left, right, top, bottom = x - w / 2, x + w / 2, y - h / 2, y + h / 2
    pts = f"{left},{top} {right - 16},{top} {right},{y} {right - 16},{bottom} {left},{bottom}"
    return f"<polygon points='{pts}' fill='#f6f8fa' stroke='{INK}' stroke-width='1.3'/>" + text(
        x - 8, y, label, size=12
    )


def accept_event(x: float, y: float, label: list[str], w: int = 190, h: int = 54) -> str:
    """UML accept event action: a box with a notch cut into its left side."""
    left, right, top, bottom = x - w / 2, x + w / 2, y - h / 2, y + h / 2
    pts = f"{left},{top} {right},{top} {right},{bottom} {left},{bottom} {left + 16},{y}"
    return f"<polygon points='{pts}' fill='#f6f8fa' stroke='{INK}' stroke-width='1.3'/>" + text(
        x + 8, y, label, size=12
    )


def diamond(x: float, y: float, r: int = 16) -> str:
    return (
        f"<polygon points='{x},{y - r} {x + r},{y} {x},{y + r} {x - r},{y}' fill='#ffffff' "
        f"stroke='{INK}' stroke-width='1.3'/>"
    )


def start(x: float, y: float) -> str:
    return f"<circle cx='{x}' cy='{y}' r='10' fill='{INK}'/>"


def flow_final(x: float, y: float) -> str:
    r = 11
    d = r * 0.7
    return (
        f"<circle cx='{x}' cy='{y}' r='{r}' fill='#ffffff' stroke='{INK}' stroke-width='1.5'/>"
        + line(x - d, y - d, x + d, y + d, width=1.5)
        + line(x - d, y + d, x + d, y - d, width=1.5)
    )


def note(x: float, y: float, w: int, h: int, lines: list[str]) -> str:
    f = 12
    return (
        f"<path d='M{x},{y} L{x + w - f},{y} L{x + w},{y + f} L{x + w},{y + h} L{x},{y + h} z' "
        f"fill='#fff8c5' stroke='{INK}' stroke-width='1'/>"
        f"<path d='M{x + w - f},{y} L{x + w - f},{y + f} L{x + w},{y + f}' "
        f"fill='none' stroke='{INK}' stroke-width='1'/>"
        + text(x + 10, y + h / 2, lines, size=11, anchor="start")
    )


def guard(x: float, y: float, lines: list[str] | str, anchor: str = "start") -> str:
    return text(x, y, lines, size=11, anchor=anchor, color=MUTED)


def activity_diagram() -> str:
    W, H = LEFT * 2 + sum(w for _, w in LANES), 1110
    dev = lane_left(0) + LANES[0][1] / 2
    scn = lane_left(1) + LANES[1][1] / 2
    rv = lane_left(2) + 105  # reviewer: main column
    rb = lane_left(2) + 270  # reviewer: block-or-revise column
    aut = lane_left(3) + LANES[3][1] / 2
    rul = lane_left(4) + LANES[4][1] / 2
    b = []
    for i, (name, w) in enumerate(LANES):
        x0 = lane_left(i)
        b.append(
            f"<rect x='{x0}' y='10' width='{w}' height='{H - 20}' fill='none' "
            f"stroke='{INK}' stroke-width='1.2'/>"
        )
        b.append(
            f"<rect x='{x0}' y='10' width='{w}' height='38' fill='#eaeef2' "
            f"stroke='{INK}' stroke-width='1.2'/>"
        )
        b.append(text(x0 + w / 2, 29, name, size=13, weight="bold"))

    # Developer proposes; merge node M1 also receives revised skills.
    b.append(start(dev, 80))
    b.append(path([(dev, 90), (dev, 113)]))
    b.append(action(dev, 140, ["Propose a skill:", "new, or a changed copy"], w=180))
    b.append(path([(dev + 90, 140), (scn - 16, 140)]))
    b.append(diamond(scn, 140))  # M1 merge
    b.append(path([(scn, 156), (scn, 193)]))
    b.append(action(scn, 220, ["Scan SKILL.md and bundled", "scripts (static; nothing runs)"]))
    b.append(path([(scn, 247), (scn, 278)]))
    b.append(
        action(
            scn,
            310,
            ["Report each match: rule,", "category, severity; context", "matches listed apart"],
            h=64,
        )
    )
    b.append(path([(scn, 342), (scn, 384)]))

    # D0: an incomplete scan never takes the no-signal path.
    b.append(diamond(scn, 400))
    b.append(guard(scn + 22, 378, ["[scan", "incomplete]"]))
    b.append(path([(scn + 16, 400), (rv - 95, 400)]))
    b.append(action(rv, 400, ["Resolve the gap, or read", "the unscanned files by hand"]))
    b.append(path([(rv, 427), (rv, 474)]))
    b.append(guard(scn - 8, 436, ["[scan", "complete]"], anchor="end"))
    b.append(path([(scn, 416), (scn, 474)]))

    # D1: severity threshold.
    b.append(diamond(scn, 490))
    b.append(guard(scn + 22, 468, ["[match with", "severity ≥ 6]"]))
    b.append(path([(scn + 16, 490), (rv - 16, 490)]))
    b.append(diamond(rv, 490))  # M3 merge
    b.append(guard(scn - 8, 522, ["[no match with", "severity ≥ 6]"], anchor="end"))
    b.append(path([(scn, 506), (scn, 548)]))
    b.append(
        action(
            scn,
            580,
            ['Record "no high-risk', 'signal" (not "safe");', "attach the report"],
            h=64,
        )
    )
    # the no-signal path still needs the reviewer's approval
    b.append(path([(scn, 612), (scn, 830), (rv - 16, 830)]))

    # Triage, then the labels go to the rule maintainer as a signal.
    b.append(path([(rv, 506), (rv, 543)]))
    b.append(
        action(
            rv,
            575,
            ["Label each high-risk finding:", "RISKY, BENIGN_CONTEXT,", "or NOT_PRESENT"],
            h=64,
        )
    )
    b.append(path([(rv, 607), (rv, 633)]))
    b.append(send_signal(rv, 660, ["Send the labels to", "the rule maintainer"]))
    b.append(path([(rv, 687), (rv, 729)]))
    b.append(diamond(rv, 745))  # D2
    b.append(guard(rv + 22, 731, "[any RISKY]"))
    b.append(path([(rv + 16, 745), (rb - 16, 745)]))
    b.append(diamond(rb, 745))  # D3: block, or ask for a change
    b.append(guard(rb + 17, 720, ["[change", "requested]"]))
    b.append(path([(rb + 16, 745), (aut - 75, 745)]))
    b.append(action(aut, 745, ["Revise the skill"], w=150))
    # rescan: back to merge M1 along the right edge of the author lane
    b.append(path([(aut + 75, 745), (aut + 85, 745), (aut + 85, 100), (scn, 100), (scn, 124)]))
    b.append(text(aut + 78, 420, "rescan", size=11, anchor="end", color=MUTED, italic=True))
    b.append(guard(rb + 8, 784, "[block]"))
    b.append(path([(rb, 761), (rb, 803)]))
    b.append(action(rb, 830, ["Block the skill;", "record the reason"], w=130))
    b.append(path([(rb, 857), (rb, 888)]))
    b.append(flow_final(rb, 900))

    b.append(guard(rv - 8, 788, "[no RISKY]", anchor="end"))
    b.append(path([(rv, 761), (rv, 814)]))
    b.append(diamond(rv, 830))  # M4 merge
    b.append(path([(rv, 846), (rv, 883)]))
    b.append(
        action(
            rv,
            915,
            ["Approve: record reviewer,", "skill version, labels,", "and the reason"],
            h=64,
        )
    )
    b.append(path([(rv, 947), (rv, 1000), (dev + 90, 1000)]))
    b.append(action(dev, 1000, ["Enable the skill"], w=180))
    b.append(path([(dev, 1027), (dev, 1053)]))
    b.append(flow_final(dev, 1065))

    # Rule maintenance runs on its own, started by the labels.
    b.append(accept_event(rul, 660, ["Labels received"]))
    b.append(path([(rul, 687), (rul, 729)]))
    b.append(diamond(rul, 745))  # D4
    b.append(guard(rul + 22, 731, "[none]"))
    b.append(path([(rul + 16, 745), (rul + 70, 745), (rul + 70, 774)]))
    b.append(flow_final(rul + 70, 786))
    b.append(guard(rul - 8, 784, ["[any false", "positive]"], anchor="end"))
    b.append(path([(rul, 761), (rul, 803)]))
    b.append(action(rul, 830, ["Log the false positives in", "the rule-change proposals"]))
    b.append(path([(rul, 857), (rul, 889)]))
    b.append(
        action(
            rul,
            920,
            ["Change the rule by pull", "request: status proposed,", "regression examples"],
            h=62,
        )
    )
    b.append(path([(rul, 951), (rul, 978)]))
    b.append(flow_final(rul, 990))

    # notes tying the workflow to the validation study
    b.append(
        note(
            dev - 90,
            470,
            180,
            96,
            [
                "No-signal path: risky",
                "skills the rules miss go",
                "this way. The miss rate",
                "in validation_recall.csv",
                "estimates how often.",
            ],
        )
    )
    b.append(line(dev + 90, 530, scn - 95, 572, dashed=True))
    b.append(
        note(
            rb - 64,
            520,
            128,
            112,
            [
                "Same labels as the",
                "validation study.",
                "1 - strict precision",
                "is the share of",
                "findings not RISKY.",
            ],
        )
    )
    b.append(line(rv + 95, 575, rb - 64, 575, dashed=True))
    return svg(W, H, b, "Activity diagram: human-in-the-loop skill risk review")


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    for name, body in (
        ("review_workflow_use_case.svg", use_case_diagram()),
        ("review_workflow_activity.svg", activity_diagram()),
    ):
        (OUT / name).write_text(body, encoding="utf-8")
        print(f"wrote {OUT / name}")


if __name__ == "__main__":
    main()
