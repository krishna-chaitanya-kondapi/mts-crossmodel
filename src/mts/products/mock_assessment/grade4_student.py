"""Dedicated reflow profile for the historical NYSED Grade 4 Math selection."""

from hashlib import sha256
from pathlib import Path
import re

import pymupdf as pdf

from .grade5_student import wrap

SOURCE_SHA256 = "88351089919b18dfc2f3dc5d64809d20aadd68d56a1dc38841a3387354b8c0f6"

FIGURES = {
    7: (74, 232),
    10: (321, 530),
    31: (75, 171),
    34: (324, 410),
    36: (98, 338),
    38: (98, 246),
    41: (114, 258),
    43: (98, 236),
}
VECTOR_CHOICES = {
    2: ("3", "9", "12", "16"),
    7: ("90 - 20 = ?", "90 - 70 = ?", "180 - 70 = ?", "180 - 110 = ?"),
    11: ("1/12", "4/12", "6/12", "8/12"),
    15: ("56/10", "15/10", "56/70", "8/70"),
    16: ("16", "17", "96", "108"),
    22: ("1 1/4", "1 3/4", "2 1/4", "2 3/4"),
    24: ("5 × 3/4 = 15/20", "4 × 2/5 = 8 × 1/5", "3 × 5/6 = 15/6", "2 × 4/8 = 8 × 1/8"),
    33: ("1/3 > 3/4", "4/5 < 1/3", "1/3 = 3/4", "3/4 < 4/5"),
    34: (
        "1,200 + 200 + 90 + 15 = 1,505",
        "1,200 + 20 + 90 + 15 = 1,325",
        "120 + 200 + 90 + 15 = 425",
        "120 + 20 + 90 + 15 = 245",
    ),
    35: (
        "1 + 1 + 2/3 + 2/3",
        "6/6 + 6/6 + 2/6 + 1/6 + 1/6",
        "1 + 1 + 3/3 + 1/3",
        "6/6 + 6/6 + 1/6 + 1/6 + 1/6",
    ),
}
STEMS = {
    2: "What value makes the equation shown below true? 3/4 = 9/?",
    22: "What is the value of the expression shown below? 4 1/4 - 2 2/4",
    11: "Which fraction can be added to 4/12 to equal 1 whole?",
    15: "Allison is training for a race. She runs 8/10 mile each day. Which fraction is equivalent to the number of miles Allison runs in 7 days?",
    16: "What is the value of 102 ÷ 6?",
    35: "Which expression is equivalent to 2 4/6?",
    42: "Two expressions are shown below. Expression A: 1/4 × 2. Expression B: 1/2 × 5. Which expression, A or B, has a value greater than 1? Be sure to include the value of each expression in your answer. Explain how you know your answer is correct.",
}


def choices_and_text(source, region, font):
    question = region["id"]
    clip = pdf.Rect(region["bounds"])
    if question == 26:
        return [("crop", clip, 0.75)]
    parts = [("text", f"{question}.", 9.2)]
    figure = FIGURES.get(question)
    inserted = False
    restored = False
    for block in source.get_text("blocks", clip=clip, sort=True):
        if block[0] < 70:
            continue
        if figure and not inserted and block[1] >= figure[1]:
            parts.append(
                (
                    "crop",
                    pdf.Rect(
                        92 if question == 31 else 135,
                        figure[0],
                        435 if question == 31 else 478,
                        figure[1],
                    ),
                    0.75,
                )
            )
            inserted = True
        text = " ".join(block[4].strip().replace("Ā", "fi").replace("ā", "fl").split())
        choice = re.match(r"^([A-D])(?:$|\s+(.+))", text) if question < 36 else None
        if choice and (
            question in VECTOR_CHOICES or choice[2] and not choice[2][0].islower()
        ):
            label = choice[1]
            body = (
                VECTOR_CHOICES[question]["ABCD".index(label)]
                if question in VECTOR_CHOICES
                else choice[2]
            )
            text = f"{label}. {body}"
            size = 9
        else:
            size = 9.2
            if question in STEMS and not text.startswith(("This question", "Answer")):
                if restored:
                    continue
                text = STEMS[question]
                restored = True
            if question == 34:
                text = text.replace("product of and .", "product of 35 and 43.")
            if text.startswith("Answer"):
                parts.append(("space", None, 25))
                text = text.replace("Answer", "Answer __________", 1)
        parts.extend(("text", line, size) for line in wrap(text, 252, size, font))
    if figure and not inserted:
        parts.append(
            (
                "crop",
                pdf.Rect(
                    92 if question == 31 else 135,
                    figure[0],
                    435 if question == 31 else 478,
                    figure[1],
                ),
                0.75,
            )
        )
    if question >= 36 and not any(kind == "space" for kind, _, _ in parts):
        parts.append(("space", None, 40))
    return parts


def _validated_page_breaks(value, selection):
    if (
        not isinstance(value, list)
        or any(type(item) is not int or item not in selection for item in value)
        or len(value) != len(set(value))
    ):
        raise ValueError("Grade 4 page breaks must reference unique selected item IDs")
    return value


def render_grade4_student(source_path, manifest, destination):
    """Render the approved source selection with Q26 in a full-width band."""
    source_bytes = Path(source_path).read_bytes()
    if (
        sha256(source_bytes).hexdigest() != SOURCE_SHA256
        or manifest["source_sha256"] != SOURCE_SHA256
    ):
        raise ValueError("Source PDF hash does not match the Grade 4 transcription")
    regions = manifest["regions"]
    selection = [1, 2, 7, 10, 11, 12, 15, 16, 22, 23, 24, 26, 29, *range(30, 45)]
    if [region["id"] for region in regions] != selection:
        raise ValueError(
            "Region sequence does not match the historical Grade 4 selection"
        )
    page_break_before = _validated_page_breaks(
        manifest.get("page_break_before", []), selection
    )
    font = pdf.Font("helv")
    with pdf.open(stream=source_bytes, filetype="pdf") as source, pdf.open() as output:
        placements = []
        left_bottom = band_top = 62
        column = 1
        y = 760
        for region in regions:
            if region["id"] in page_break_before:
                if not output:
                    raise ValueError(
                        "A Grade 4 page break cannot precede the first output page"
                    )
                if len(output) >= 4:
                    raise ValueError("Grade 4 student worksheet exceeds four pages")
                page = output.new_page(width=612, height=792)
                page.insert_text((30, 30), "MTS | " + manifest["title"], fontsize=11)
                page.insert_text(
                    (30, 49),
                    "Name: __________________________  Date: ______________",
                    fontsize=9,
                )
                column = 0
                y = left_bottom = band_top = 62
            source_index = region["source_page"] - 1
            parts = choices_and_text(source[source_index], region, font)
            full_width = region["id"] == 26
            amount = (
                sum(
                    (
                        value.height * size + 8
                        if kind == "crop"
                        else 11.5 if kind == "text" else size
                    )
                    for kind, value, size in parts
                )
                + 6
            )
            if full_width:
                y = max(y, left_bottom)
            elif column == 0 and y + amount > 752:
                left_bottom = y
                column = 1
                y = band_top
            if y + amount > 752:
                if len(output) >= 4:
                    raise ValueError("Grade 4 student worksheet exceeds four pages")
                page = output.new_page(width=612, height=792)
                page.insert_text((30, 30), "MTS | " + manifest["title"], fontsize=11)
                column = 0
                y = left_bottom = band_top = 62
            x = 30 if full_width or column == 0 else 316
            placements.append(
                dict(
                    item=region["id"],
                    page=len(output),
                    column="full" if full_width else column + 1,
                    y=y,
                    height=amount,
                )
            )
            for kind, value, size in parts:
                if kind == "text":
                    page.insert_text((x, y + size), value, fontsize=size)
                    y += 11.5
                elif kind == "crop":
                    target = pdf.Rect(
                        x, y + 4, x + value.width * size, y + 4 + value.height * size
                    )
                    page.show_pdf_page(target, source, source_index, clip=value)
                    y += value.height * size + 8
                else:
                    y += size
            y += 6
            if full_width:
                left_bottom = band_top = y
                column = 0
        for index, rendered_page in enumerate(output, 1):
            rendered_page.insert_text(
                (548, 776), f"{index} / {len(output)}", fontsize=8
            )
        output.save(destination, garbage=4, deflate=True)
    return placements
