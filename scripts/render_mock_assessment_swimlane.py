"""Render the implemented Mock Assessment flow using the established six-lane design."""

import argparse
from html import escape
from pathlib import Path
import shutil
import xml.etree.ElementTree as ET

import pymupdf

ROOT = Path(__file__).resolve().parents[1]
W, H = 1680, 2560
LANE_X = [100 + 262 * i for i in range(6)]
CENTERS = [x + 125 for x in LANE_X]
BLUE = "#e0edf8"
INK = "#17365b"
NODES = {
    "request": (0, 210, ["Approved scope", "Math G4/G5 or ELA G6"], "process"),
    "resume": (
        2,
        310,
        ["Initialize or resume", "checkpoint + saved profile"],
        "process",
    ),
    "assets": (
        4,
        410,
        ["Original sources + goldens", "restore only when needed"],
        "process",
    ),
    "validate": (
        3,
        510,
        ["Validate source + blueprint", "selection, dates, print limits"],
        "process",
    ),
    "spec": (2, 610, ["Validate saved RunSpec", "record runtime estimate"], "process"),
    "prerun": (4, 700, ["01-PreRun", "RunSpec JSON + PDF"], "storage"),
    "render": (
        3,
        820,
        ["Generate student + key", "dedicated Math / ELA profiles"],
        "process",
    ),
    "structure": (
        3,
        920,
        ["Fresh structural checks", "items, keys, bounds, pages"],
        "process",
    ),
    "match": (2, 1030, ["Exact baseline", "match?"], "gate"),
    "fresh": (
        1,
        1155,
        ["Fresh independent review", "answers, source, every page"],
        "process",
    ),
    "reuse": (
        4,
        1155,
        ["Reuse completed reviews", "only with intact exact proof"],
        "success",
    ),
    "repair": (
        1,
        1270,
        ["Repair content or layout", "re-render and reverify"],
        "repair",
    ),
    "quality": (2, 1385, ["Per-run quality", "all PASS?"], "gate"),
    "artifacts": (
        4,
        1485,
        ["02-Run PDFs / 03-PostRun", "QA, hashes, runtime, run log"],
        "storage",
    ),
    "dev": (2, 1610, ["76 criteria PASS", "revision valid?"], "gate"),
    "blocked": (
        4,
        1610,
        ["NOT_DONE checkpoint", "evidence + exact next actions"],
        "repair",
    ),
    "package": (
        2,
        1725,
        ["Ready for acceptance", "report + review package"],
        "success",
    ),
    "approve": (0, 1840, ["Human approval", "Exact student + key?"], "current"),
    "guard": (3, 1960, ["Approval + hashes", "quality valid?"], "gate"),
    "publish": (
        3,
        2075,
        ["Stage, archive, publish", "preserve others + readback"],
        "process",
    ),
    "recover": (
        4,
        2075,
        ["Failure: restore prior set", "retain durable recovery proof"],
        "repair",
    ),
    "ready": (
        4,
        2190,
        ["Verified PrintReady set", "publication receipt saved"],
        "success",
    ),
    "print": (
        5,
        2305,
        ["Existing external printing", "independent of this workflow"],
        "external",
    ),
    "retro": (
        1,
        2405,
        ["Retrospective / improve", "feed the next approved run"],
        "process",
    ),
    "handover": (
        4,
        2405,
        ["Archive + checkpoint", "GitHub / Copilot takeover"],
        "storage",
    ),
}
svg = []


def emit(value):
    svg.append(value)


def text(x, y, value, size=17, fill=INK, anchor="middle", weight="normal"):
    emit(
        f'<text x="{x}" y="{y}" font-size="{size}" fill="{fill}" text-anchor="{anchor}" font-weight="{weight}">{escape(value)}</text>'
    )


def position(name, side):
    lane, y, _, kind = NODES[name]
    x = CENTERS[lane]
    halfh = 46 if kind in ("gate", "current") else 35
    return {
        "top": (x, y - halfh),
        "bottom": (x, y + halfh),
        "left": (x - 109, y),
        "right": (x + 109, y),
    }[side]


def arrow(points, color="#64748b", dashed=False):
    emit(
        '<polyline points="'
        + " ".join(f"{x},{y}" for x, y in points)
        + '" fill="none" stroke="'
        + color
        + '" stroke-width="2.2" stroke-linejoin="round"'
        + (' stroke-dasharray="7 5"' if dashed else "")
        + "/>"
    )
    x, y = points[-1]
    px, py = points[-2]
    if x == px:
        sign = 1 if y > py else -1
        vertices = [(x, y), (x - 5, y - sign * 10), (x + 5, y - sign * 10)]
    else:
        sign = 1 if x > px else -1
        vertices = [(x, y), (x - sign * 10, y - 5), (x - sign * 10, y + 5)]
    emit(
        '<polygon points="'
        + " ".join(f"{a},{b}" for a, b in vertices)
        + '" fill="'
        + color
        + '"/>'
    )


def connect(a, b, label=None):
    start = position(a, "bottom")
    end = position(b, "top")
    middle = (start[1] + end[1]) / 2
    pts = (
        [start, end]
        if start[0] == end[0]
        else [start, (start[0], middle), (end[0], middle), end]
    )
    arrow(pts)
    if label:
        text(start[0] + 22, middle - 7, label, 14, anchor="start")


def tag(x, y, value, color="#64748b"):
    width = len(value) * 7.5 + 16
    emit(
        f'<rect x="{x-width/2}" y="{y-15}" width="{width}" height="21" rx="4" fill="#fff"/>'
    )
    text(x, y, value, 14, color)


emit(
    f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="Implemented MTS Mock Assessment end-to-end process flow with six responsibility swimlanes">'
)
emit("<title>MTS Mock Assessment — implemented end-to-end workflow</title>")
emit(
    "<desc>Six vertical lanes show human, AI, orchestrator, code, storage and external printing responsibilities across PreRun, Run and PostRun. Exact reviewed baselines may reuse completed reviews. Otherwise fresh review and repair are required. All mandatory criteria and explicit human approval precede production release.</desc>"
)
emit(
    f'<rect width="{W}" height="{H}" fill="#fff"/><g font-family="Arial, Helvetica, sans-serif">'
)
text(
    28,
    41,
    "MTS | Mock Assessment — end-to-end process flow",
    29,
    anchor="start",
    weight="bold",
)
text(
    28,
    72,
    "Implemented historical source-based benchmarks · Math Grades 4/5 + ELA Grade 6",
    18,
    anchor="start",
)
text(1652, 72, "Checkpoint 27 | 18 Nov 2026", 16, "#64748b", anchor="end")
text(
    1652,
    101,
    "76/76 mandatory verified · current position: human review · no production publication",
    16,
    "#166534",
    anchor="end",
)
lanes = [
    "Human",
    "AI / review agent",
    "Harness / orchestrator",
    "Code / PDF tools",
    "Storage / evidence",
    "External automation",
]
for i, (x, label) in enumerate(zip(LANE_X, lanes)):
    emit(
        f'<rect x="{x}" y="118" width="250" height="2335" rx="6" fill="'
        + ("#f8fafc" if i % 2 == 0 else "#f1f5f9")
        + '" stroke="#dbe3ed"/>'
    )
    emit(f'<rect x="{x}" y="118" width="250" height="40" rx="5" fill="#294c70"/>')
    text(x + 125, 144, label, 18, "white")
for y, h, label, color in [
    (175, 570, "01 PreRun", "#dbeafe"),
    (770, 760, "02 Run", "#d1fae5"),
    (1555, 898, "03 PostRun", "#ede9fe"),
]:
    emit(f'<rect x="16" y="{y}" width="64" height="{h}" rx="7" fill="{color}"/>')
    emit(
        f'<text transform="translate(55 {y+h/2}) rotate(-90)" font-size="21" text-anchor="middle" font-weight="bold" fill="#334155">{label}</text>'
    )
# Main path and branches. Connectors render below the nodes.
for a, b in [
    ("request", "resume"),
    ("resume", "assets"),
    ("assets", "validate"),
    ("validate", "spec"),
    ("spec", "prerun"),
    ("prerun", "render"),
    ("render", "structure"),
    ("structure", "match"),
]:
    connect(a, b)
arrow([position("match", "left"), (487, 1030), position("fresh", "top")])
tag(530, 1014, "No exact match")
arrow([position("match", "right"), (1273, 1030), position("reuse", "top")])
tag(1095, 1014, "Exact match")
arrow(
    [position("fresh", "bottom"), (487, 1210), (749, 1210), position("quality", "top")]
)
arrow([position("reuse", "bottom"), (1273, 1385), position("quality", "right")])
tag(1100, 1368, "Reviewed baseline PASS", "#166534")
arrow(
    [
        position("quality", "left"),
        (620, 1385),
        (620, 1270),
        position("repair", "right"),
    ],
    "#b45309",
    True,
)
tag(620, 1356, "Fail", "#b45309")
arrow(
    [
        position("repair", "left"),
        (94, 1270),
        (94, 768),
        (1011, 768),
        position("render", "top"),
    ],
    "#b45309",
    True,
)
tag(486, 757, "Repair loop: render and check again", "#b45309")
connect("quality", "artifacts", "Pass")
connect("artifacts", "dev")
arrow([position("dev", "right"), position("blocked", "left")], "#b45309", True)
tag(1000, 1594, "Fail / missing evidence", "#b45309")
connect("dev", "package", "Pass")
connect("package", "approve")
arrow(
    [
        position("approve", "right"),
        (356, 1840),
        (356, 1270),
        position("repair", "left"),
    ],
    "#b45309",
    True,
)
tag(354, 1690, "Changes requested", "#b45309")
connect("approve", "guard")
tag(740, 1892, "Explicit approval of both PDF hashes", "#166534")
arrow(
    [
        position("guard", "right"),
        (1142, 1960),
        (1142, 1648),
        (1273, 1648),
        position("blocked", "bottom"),
    ],
    "#b45309",
    True,
)
tag(1220, 1900, "Invalid: stop", "#b45309")
connect("guard", "publish", "Valid")
arrow([position("publish", "right"), position("recover", "left")], "#b45309", True)
connect("publish", "ready", "Verified")
connect("ready", "print")
connect("ready", "handover")
arrow([position("handover", "left"), position("retro", "right")])
# A concise explicit preflight stop, routed through the otherwise idle external lane.
arrow(
    [
        position("validate", "right"),
        (1668, 510),
        (1668, 1610),
        position("blocked", "right"),
    ],
    "#b45309",
    True,
)
tag(1515, 493, "Invalid source / unsupported scope", "#b45309")
# Render labelled steps and gates.
for name, (lane, y, lines, kind) in NODES.items():
    x = CENTERS[lane]
    if kind in ("gate", "current"):
        emit(
            f'<polygon points="{x},{y-46} {x+109},{y} {x},{y+46} {x-109},{y}" fill="#fef3c7" stroke="'
            + ("#1d4ed8" if kind == "current" else "#b45309")
            + '" stroke-width="'
            + ("3.5" if kind == "current" else "1.7")
            + '"/>'
        )
        for index, line in enumerate(lines):
            text(
                x,
                y - 5 + index * 22,
                line,
                14,
                weight="bold" if kind == "current" else "normal",
            )
    else:
        fill, stroke = {
            "success": ("#dcfce7", "#4d9470"),
            "repair": ("#fff1e6", "#b45309"),
            "storage": ("#eef2ff", "#7185ad"),
            "external": ("#f8fafc", "#64748b"),
        }.get(kind, (BLUE, "#537a9f"))
        emit(
            f'<rect x="{x-109}" y="{y-35}" width="218" height="70" rx="7" fill="{fill}" stroke="{stroke}" stroke-width="1.6"'
            + (' stroke-dasharray="6 4"' if kind == "external" else "")
            + "/>"
        )
        for index, line in enumerate(lines):
            font = pymupdf.Font("hebo" if index == 0 else "helv")
            size = min(16, 196 / font.text_length(line, fontsize=1))
            text(
                x,
                y - 5 + index * 23,
                line,
                size,
                weight="bold" if index == 0 else "normal",
            )
# Notes clarify the cache boundary and existing human authorization.
text(225, 274, "Current scope already authorized", 13, "#64748b")
text(1535, 710, "Every structural check runs again.", 15, "#475569")
text(1535, 738, "Fresh semantic / visual review", 15, "#475569")
text(1535, 763, "is agent-driven when needed.", 15, "#475569")
for i, line in enumerate(
    [
        "Exact match means source,",
        "canonical manifests, code,",
        "renderer, all page pixels",
        "and evidence hashes match.",
    ]
):
    text(1535, 1117 + i * 23, line, 15, "#475569")
text(225, 1945, "CURRENT: awaiting human review", 14, "#1d4ed8", weight="bold")
text(
    838,
    2488,
    "Blue: activity   ·   Amber diamond: gate   ·   Green: verified result   ·   Amber return arrows: repair / stop / recovery",
    16,
    "#475569",
)
text(
    838,
    2516,
    "Weekly Practice stays independent. Broader diagnostic, custom and generated modes remain deferred.",
    16,
    "#475569",
)
text(
    838,
    2543,
    "No production release without artifact-specific human approval. Printing remains external; live Drive publication has not been performed.",
    15,
    "#475569",
)
emit("</g></svg>")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--export-dir", type=Path, required=True)
    args = parser.parse_args()
    data = "\n".join(svg) + "\n"
    ET.fromstring(data)
    target = ROOT / "specs/generate_mock_assessment/end-to-end-swimlane.svg"
    target.write_bytes(data.encode())
    args.export_dir.mkdir(parents=True, exist_ok=True)
    stem = args.export_dir / "MTS-Mock-Assessment-End-to-End-Swimlane"
    shutil.copyfile(target, stem.with_suffix(".svg"))
    image = pymupdf.open(stream=data.encode(), filetype="svg")
    pdf = pymupdf.open("pdf", image.convert_to_pdf())
    pdf.save(stem.with_suffix(".pdf"), garbage=4, deflate=True)
    pdf[0].get_pixmap(matrix=pymupdf.Matrix(1, 1), alpha=False).save(
        stem.with_suffix(".png")
    )
    print(f"Created SVG, PDF and PNG in {args.export_dir}")


if __name__ == "__main__":
    main()
