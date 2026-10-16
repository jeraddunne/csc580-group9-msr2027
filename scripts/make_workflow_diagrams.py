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
        "U4": (630, 420, ["Triage each finding", "(RISKY / BENIGN / NOT_PRESENT)"]),
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

LANES = ["Developer", "Scanner (automated)", "Security reviewer", "Skill author", "Rule maintainer"]
LANE_W = 210
LEFT = 10


def lane_x(i: int) -> float:
    return LEFT + LANE_W * i + LANE_W / 2


def action(x: float, y: float, label: list[str], w: int = 190, h: int = 54) -> str:
    return (
        f"<rect x='{x - w / 2}' y='{y - h / 2}' width='{w}' height='{h}' rx='14' fill='#f6f8fa' "
        f"stroke='{INK}' stroke-width='1.3'/>" + text(x, y, label, size=12)
    )


def diamond(x: float, y: float, r: int = 16) -> str:
    return (
        f"<polygon points='{x},{y - r} {x + r},{y} {x},{y + r} {x - r},{y}' fill='#ffffff' "
        f"stroke='{INK}' stroke-width='1.3'/>"
    )


def start(x: float, y: float) -> str:
    return f"<circle cx='{x}' cy='{y}' r='10' fill='{INK}'/>"


def final(x: float, y: float) -> str:
    return (
        f"<circle cx='{x}' cy='{y}' r='12' fill='#ffffff' stroke='{INK}' stroke-width='1.5'/>"
        f"<circle cx='{x}' cy='{y}' r='7' fill='{INK}'/>"
    )


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


def activity_diagram() -> str:
    W, H = LEFT * 2 + LANE_W * len(LANES), 1010
    dev, scn, rev, aut, rul = (lane_x(i) for i in range(5))
    b = []
    for i, name in enumerate(LANES):
        x0 = LEFT + LANE_W * i
        b.append(
            f"<rect x='{x0}' y='10' width='{LANE_W}' height='{H - 20}' fill='none' "
            f"stroke='{INK}' stroke-width='1.2'/>"
        )
        b.append(
            f"<rect x='{x0}' y='10' width='{LANE_W}' height='38' fill='#eaeef2' "
            f"stroke='{INK}' stroke-width='1.2'/>"
        )
        b.append(text(x0 + LANE_W / 2, 29, name, size=13, weight="bold"))

    # Developer proposes; merge node M1 also receives revised skills.
    b.append(start(dev, 80))
    b.append(path([(dev, 90), (dev, 113)]))
    b.append(action(dev, 140, ["Propose a skill:", "new, or a changed copy"]))
    b.append(path([(dev + 95, 140), (scn - 16, 140)]))
    b.append(diamond(scn, 140))  # M1 merge
    b.append(path([(scn, 156), (scn, 193)]))
    b.append(action(scn, 220, ["Scan SKILL.md and bundled", "scripts (static; nothing runs)"]))
    b.append(path([(scn, 247), (scn, 283)]))
    b.append(action(scn, 310, ["Report each rule match:", "rule, category, severity"]))
    b.append(path([(scn, 337), (scn, 374)]))
    b.append(diamond(scn, 390))  # D1
    b.append(text(scn + 8, 424, "[no match with", size=11, anchor="start", color=MUTED))
    b.append(text(scn + 8, 438, "severity ≥ 6]", size=11, anchor="start", color=MUTED))
    b.append(path([(scn, 406), (scn, 473)]))
    b.append(action(scn, 500, ["Record: no high-risk", "signal; attach report"]))
    b.append(text(scn + 22, 362, "[match with", size=11, anchor="start", color=MUTED))
    b.append(text(scn + 22, 376, "severity ≥ 6]", size=11, anchor="start", color=MUTED))
    b.append(path([(scn + 16, 390), (rev - 95, 390)]))
    b.append(
        action(rev, 390, ["Label each finding:", "RISKY, BENIGN_CONTEXT,", "or NOT_PRESENT"], h=64)
    )
    b.append(path([(rev, 422), (rev, 474)]))
    b.append(diamond(rev, 490))  # D2
    b.append(text(rev + 24, 506, "[any RISKY]", size=11, anchor="start", color=MUTED))
    b.append(text(rev + 24, 520, "block, or ask", size=11, anchor="start", color=MUTED))
    b.append(text(rev + 24, 534, "for a change", size=11, anchor="start", color=MUTED))
    b.append(path([(rev + 16, 490), (aut - 95, 490)]))
    b.append(action(aut, 490, ["Revise the skill"]))
    # loop back to merge M1, along the right edge of the author lane
    b.append(path([(aut + 95, 490), (aut + 100, 490), (aut + 100, 100), (scn, 100), (scn, 124)]))
    b.append(text(aut + 92, 300, "rescan", size=11, anchor="end", color=MUTED, italic=True))
    b.append(text(rev - 8, 540, "[no RISKY]", size=11, anchor="end", color=MUTED))
    b.append(path([(rev, 506), (rev, 573)]))
    b.append(action(rev, 600, ["Approve; record labels", "and the reason"]))
    b.append(path([(rev, 627), (rev, 664)]))
    b.append(f"<rect x='{rev - 90}' y='664' width='180' height='6' fill='{INK}'/>")  # fork
    # fork branch 1: to merge M2 in the Developer lane
    b.append(path([(rev - 60, 670), (rev - 60, 720), (dev + 16, 720)]))
    # no-signal path also goes to M2
    b.append(path([(scn, 527), (scn, 560), (dev, 560), (dev, 704)]))
    b.append(diamond(dev, 720))  # M2 merge
    b.append(path([(dev, 736), (dev, 773)]))
    b.append(action(dev, 800, ["Enable the skill"]))
    b.append(path([(dev, 827), (dev, 858)]))
    b.append(final(dev, 872))
    # fork branch 2: rule maintainer
    b.append(path([(rev + 60, 670), (rev + 60, 700), (rul, 700), (rul, 724)]))
    b.append(diamond(rul, 740))  # D3
    b.append(text(rul + 22, 726, "[none]", size=11, anchor="start", color=MUTED))
    b.append(path([(rul + 16, 740), (rul + 70, 740), (rul + 70, 769)]))
    b.append(flow_final(rul + 70, 781))
    b.append(text(rul - 8, 774, "[any false", size=11, anchor="end", color=MUTED))
    b.append(text(rul - 8, 788, "positive]", size=11, anchor="end", color=MUTED))
    b.append(path([(rul, 756), (rul, 813)]))
    b.append(action(rul, 840, ["Log the false positives in", "the rule-change proposals"]))
    b.append(path([(rul, 867), (rul, 893)]))
    b.append(
        action(
            rul,
            920,
            ["Change the rule by pull", "request: status proposed,", "regression examples"],
            h=62,
        )
    )
    b.append(path([(rul, 951), (rul, 969)]))
    b.append(flow_final(rul, 981))

    # notes tying the workflow to the validation study
    b.append(
        note(
            scn - 98,
            610,
            196,
            84,
            [
                "No-signal path: risky skills",
                "the rules miss go this way.",
                "The validation miss rate",
                "(validation_recall.csv)",
                "estimates how often.",
            ],
        )
    )
    b.append(line(scn + 60, 610, scn + 60, 527, dashed=True))
    b.append(
        note(
            rev - 98,
            140,
            196,
            108,
            [
                "Triage uses the same labels",
                "as the validation study",
                "(ANNOTATION_GUIDELINE.md).",
                "Rule precision estimates how",
                "many findings a reviewer will",
                "clear as false alarms.",
            ],
        )
    )
    b.append(line(rev, 248, rev, 358, dashed=True))
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
