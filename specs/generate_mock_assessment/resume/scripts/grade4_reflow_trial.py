"""Source-based Grade 4 compact layout diagnostic."""
import json
from pathlib import Path
import re
import sys

import pymupdf as pdf

sys.path.insert(0, str(Path("work/mts-crossmodel/src").resolve()))
from mts.products.mock_assessment.grade5_student import wrap

FIGURES = {
    7: (74, 232), 10: (321, 530),
    31: (75, 171), 34: (324, 410), 36: (98, 338), 38: (98, 246),
    41: (114, 258), 43: (98, 236),
}
VECTOR_CHOICES = {
    2: ("3", "9", "12", "16"), 7: ("90 - 20 = ?", "90 - 70 = ?", "180 - 70 = ?", "180 - 110 = ?"),
    11: ("1/12", "4/12", "6/12", "8/12"), 15: ("56/10", "15/10", "56/70", "8/70"),
    16: ("16", "17", "96", "108"), 22: ("1 1/4", "1 3/4", "2 1/4", "2 3/4"),
    24: ("5 × 3/4 = 15/20", "4 × 2/5 = 8 × 1/5", "3 × 5/6 = 15/6", "2 × 4/8 = 8 × 1/8"),
    33: ("1/3 > 3/4", "4/5 < 1/3", "1/3 = 3/4", "3/4 < 4/5"),
    34: ("1,200 + 200 + 90 + 15 = 1,505", "1,200 + 20 + 90 + 15 = 1,325", "120 + 200 + 90 + 15 = 425", "120 + 20 + 90 + 15 = 245"),
    35: ("1 + 1 + 2/3 + 2/3", "6/6 + 6/6 + 2/6 + 1/6 + 1/6", "1 + 1 + 3/3 + 1/3", "6/6 + 6/6 + 1/6 + 1/6 + 1/6"),
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

font = pdf.Font("helv")
regions = json.loads(Path("outputs/grade4-component-regions.json").read_text())["regions"]
source_path = "work/golden/NY_Math_Grade4_2024_Released_Test_Questions.pdf"


def choices_and_text(source, region):
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
            parts.append(("crop", pdf.Rect(92 if question == 31 else 135, figure[0], 435 if question == 31 else 478, figure[1]), 0.75))
            inserted = True
        text = " ".join(block[4].strip().replace("Ā", "fi").replace("ā", "fl").split())
        choice = re.match(r"^([A-D])(?:$|\s+(.+))", text) if question < 36 else None
        if choice and (question in VECTOR_CHOICES or choice[2] and not choice[2][0].islower()):
            label = choice[1]
            body = VECTOR_CHOICES[question]["ABCD".index(label)] if question in VECTOR_CHOICES else choice[2]
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
        parts.append(("crop", pdf.Rect(92 if question == 31 else 135, figure[0], 435 if question == 31 else 478, figure[1]), 0.75))
    if question >= 36 and not any(kind == "space" for kind, _, _ in parts):
        parts.append(("space", None, 40))
    return parts


with pdf.open(source_path) as source, pdf.open() as output:
    placements = []
    left_bottom = band_top = 62
    column = 1
    y = 760
    for region in regions:
        source_index = region["source_page"] - 1
        parts = choices_and_text(source[source_index], region)
        full_width = region["id"] == 26
        amount = sum(value.height * size + 8 if kind == "crop" else 11.5 if kind == "text" else size
                     for kind, value, size in parts) + 6
        if full_width:
            y = max(y, left_bottom)
        elif column == 0 and y + amount > 752:
            left_bottom = y
            column = 1
            y = band_top
        if y + amount > 752:
            page = output.new_page(width=612, height=792)
            page.insert_text((30, 36), "Grade 4 Mathematics | NYSED 2024 | Layout diagnostic", fontsize=11)
            column = 0
            y = left_bottom = band_top = 62
        x = 30 if full_width or column == 0 else 316
        placements.append(dict(item=region["id"], page=len(output), column="full" if full_width else column + 1, y=y, height=amount))
        for kind, value, size in parts:
            if kind == "text":
                page.insert_text((x, y + size), value, fontsize=size)
                y += 11.5
            elif kind == "crop":
                target = pdf.Rect(x, y + 4, x + value.width * size, y + 4 + value.height * size)
                page.show_pdf_page(target, source, source_index, clip=value)
                y += value.height * size + 8
            else:
                y += size
        y += 6
        if full_width:
            left_bottom = band_top = y
            column = 0
    output.save("work/grade4-reflow-diagnostic.pdf", garbage=4, deflate=True)
    assert len(placements) == 28
    print(f"{len(placements)} question blocks, {len(output)} pages")
    Path("outputs/grade4-reflow-evidence.json").write_text(json.dumps(
        dict(pages=len(output), maximum_pages=4, placements=placements, source_fidelity="NOT_VERIFIED",
             golden="MTS-NY-Math-Grade4-2024-Worksheet-REVIEW.pdf"), indent=2) + "\n")
    for i, page in enumerate(output, 1):
        page.get_pixmap(alpha=False).save(f"work/grade4-reflow-{i}.png")
