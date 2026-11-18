"""Grade 5 source reflow experiment. Output is a layout diagnostic, not a worksheet."""
from pathlib import Path
import json
import re

import pymupdf as pdf

SOURCE = Path("work/golden/NY_Math_Grade5_2024_Released_Test_Questions.pdf")
REGIONS = json.loads(Path("outputs/grade5-component-regions.json").read_text())["regions"]
FIGURES = {
    3: (75, 158), 9: (75, 307), 39: (112, 328),
    40: (141, 299), 43: (98, 297),
}
# The released PDF draws these formulas as paths outside its text layer.
RESTORED_STEMS = {
    2: "Which expression is equivalent to 5 × 3/4?",
    7: "A group of 4 gold miners found 10 ounces of gold. The miners shared the gold equally. How much gold, in ounces, did each miner receive?",
    10: "Steven has 3 cups of raisins. He shares all the raisins equally among himself and his friends. If each person gets 1/4 cup of raisins, how many people, in total, get raisins?",
    27: "What is the value of the expression 1/7 ÷ 5?",
    28: "Marcel has 2 1/3 cups of milk. He uses 2/3 cup for his cereal and 1 1/4 cups for a pancake recipe. How much milk, in cups, does Marcel have remaining?",
    30: "What is the area, in square units, of a rectangle with side lengths 3 3/4 units and 9 1/2 units?",
    32: "What is the value of the expression shown below? 1/2 + 2/3 − 1/4",
    34: "Elsie has two equal-sized bags of rice. One bag is 1/3 full, and the other bag is 1/5 full. She combines the rice into one of the bags. What fraction of a full bag of rice does Elsie now have after combining the rice?",
    37: "A family takes a cake to a party. When the family is ready to leave the party, 3/4 of the cake is left. The family leaves 1/2 of the leftover cake at the party and takes the remaining cake home. What fraction of all of the cake does the family take home?",
    41: "Rosa and Steve each have a baseball card collection. Steve has 1/8 as many baseball cards in his collection as Rosa. Who has more baseball cards? Be sure to include what you know about fractions in your answer. Explain your answer.",
    42: "A student incorrectly wrote the number three hundred sixty-two and four hundred eight thousandths in expanded form as shown below. (3 × 100) + (6 × 10) + (2 × 1) + (4 × 1/10) + (8 × 1/100) What error did the student make when writing the number in expanded form? Be sure to include the correct number in standard form in your answer. Explain your answer.",
}

FONT = pdf.Font("helv")


def wrap(text, width, size):
    line = ""
    for word in text.split():
        candidate = f"{line} {word}".strip()
        if line and FONT.text_length(candidate, fontsize=size) > width:
            yield line
            line = word
        else:
            line = candidate
    if line:
        yield line


def extract(page, region):
    question = region["id"]
    figure = FIGURES.get(question)
    blocks = [
        b for b in page.get_text("blocks", clip=pdf.Rect(region["bounds"]), sort=True)
        if b[0] >= 70
    ]
    parts = [("text", f"{question}.", 9.2)]
    restored = False
    for index, block in enumerate(blocks):
        if figure and block[1] >= figure[1] and not any(p[0] == "figure" for p in parts):
            # A wide crop preserves labels omitted by the PDF text layer.
            parts.append(("figure", pdf.Rect(154, figure[0], 490 if question == 43 else 432, figure[1]), 0.70 if question == 43 else 0.75))
        text = block[4].strip().replace("Ā", "fi")
        choice = re.fullmatch(r"([A-D])(?:[^\S\n]*\n(.*))?", text, flags=re.S)
        if choice:
            label, body = choice.groups()
            if not body:
                # Choice labels are text, while the expressions are embedded paths.
                top = block[1] - 8
                bottom = min(block[3] + 9, blocks[index + 1][1] - 8) if index + 1 < len(blocks) else block[3] + 9
                parts.append(("formula", pdf.Rect(70, top, 310, bottom), 0.85))
                continue
            text = f"{label}. {body}"
        elif figure and figure[0] <= block[1] < figure[1]:
            continue
        if text.startswith("Answer"):
            parts.append(("space", None, 18))
            text = "Answer ________ " + text.removeprefix("Answer").strip()
        elif not choice and question in RESTORED_STEMS and not text.startswith("This question"):
            if restored:
                continue
            text = RESTORED_STEMS[question]
            restored = True
        elif question == 40:
            text = re.sub(r"length of\s+foot", "length of 1/2 foot", text)
        size = 9 if choice else 9.2
        parts.extend(("text", line, size) for line in wrap(text, 252, size))
    if question >= 36:
        parts.append(("space", None, 27))
    return parts


def height(part):
    kind, value, size = part
    if kind in {"figure", "formula"}:
        return value.height * size + 10
    return 11.5 if kind == "text" else size


with pdf.open(SOURCE) as source, pdf.open() as book:
    column = 1
    y = 760
    placement = []
    for region in REGIONS:
        source_index = region["source_page"] - 1
        parts = extract(source[source_index], region)
        block_height = sum(map(height, parts)) + 6
        if block_height > 690:
            raise ValueError(f"Question {region['id']} exceeds an empty column")
        if y + block_height > 754:
            if column == 0:
                column = 1
            else:
                page = book.new_page(width=612, height=792)
                page.insert_text((30, 38), "Grade 5 Mathematics | Layout diagnostic", fontsize=12)
                column = 0
            y = 64
        x = 30 if column == 0 else 316
        placement.append(dict(id=region["id"], page=len(book), column=column + 1, y=y, height=block_height))
        for part in parts:
            kind, value, size = part
            if kind == "text":
                page.insert_text((x, y + size), value.replace("−", "-"), fontsize=size)
            elif kind in {"figure", "formula"}:
                target = pdf.Rect(x, y + 5, x + value.width * size, y + 5 + value.height * size)
                page.show_pdf_page(target, source, source_index, clip=value)
            y += height(part)
        y += 6
    book.save("work/grade5-reflow-diagnostic.pdf", garbage=4, deflate=True)
    result = dict(pages=len(book), ceiling=4, placements=placement,
                  academic_status="NOT_VERIFIED",
                  defects=["Vector-only choices are cropped. Prompt notation and crop completeness still need independent review.",
                           "Figure crop bounds and clearance require visual validation.",
                           "Constructed-response label and spacing need source comparison."])
    Path("outputs/grade5-reflow-evidence.json").write_text(json.dumps(result, indent=2) + "\n")
    print(f"{len(placement)} regions on {len(book)} pages")




