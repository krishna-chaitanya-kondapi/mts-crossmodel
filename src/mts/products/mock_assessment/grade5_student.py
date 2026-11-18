"""Dedicated reflow profile for the historical NYSED Grade 5 Math selection."""

from hashlib import sha256
from pathlib import Path
import re

import pymupdf

SOURCE_SHA256 = "96bc4dca01185cda99056c98391ac85d41ecf7595b2b3ec29f7595b7e7b91f93"
FIGURES = {3: (75, 158), 9: (75, 307), 39: (112, 328), 40: (141, 299), 43: (98, 297)}

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


VECTOR_CHOICES = {
    2: (
        "5/1 + 3/4",
        "5/1 - 3/4",
        "3/4 + 3/4 + 3/4 + 3/4 + 3/4",
        "3/4 × 3/4 × 3/4 × 3/4 × 3/4",
    ),
    7: ("1/4", "4/10", "2 2/10", "2 1/2"),
    10: ("1", "4", "7", "12"),
    16: ("0.04 > 0.14", "0.83 > 0.92", "0.27 < 0.36", "0.52 < 0.49"),
    27: ("1/35", "1/12", "5/7", "6/7"),
    28: ("5/12", "7/12", "1 1/12", "1 11/12"),
    30: ("13 1/4", "27 3/8", "35 5/8", "47 1/2"),
    32: ("2/1", "4/9", "11/12", "17/12"),
    34: ("1/2", "1/4", "2/15", "8/15"),
}


def wrap(text, width, size, font):
    line = ""
    for word in text.split():
        candidate = f"{line} {word}".strip()
        if line and font.text_length(candidate, fontsize=size) > width:
            yield line
            line = word
        else:
            line = candidate
    if line:
        yield line


def extract(page, region, font):
    question = region["id"]
    figure = FIGURES.get(question)
    blocks = [
        b
        for b in page.get_text("blocks", clip=pymupdf.Rect(region["bounds"]), sort=True)
        if b[0] >= 70
    ]
    parts = [("text", f"{question}.", 9.2)]
    restored = False
    has_answer_line = False
    for block in blocks:
        if (
            figure
            and block[1] >= figure[1]
            and not any(p[0] == "figure" for p in parts)
        ):
            # A wide crop preserves labels omitted by the PDF text layer.
            parts.append(
                (
                    "figure",
                    pymupdf.Rect(
                        154, figure[0], 490 if question == 43 else 432, figure[1]
                    ),
                    0.70 if question == 43 else 0.75,
                )
            )
        text = block[4].strip().replace("Ā", "fi")
        choice = re.fullmatch(r"([A-D])(?:[^\S\n]*\n(.*))?", text, flags=re.S)
        if choice:
            label, body = choice.groups()
            if not body:
                body = VECTOR_CHOICES[question]["ABCD".index(label)]
            text = f"{label}. {body}"
        elif figure and figure[0] <= block[1] < figure[1]:
            continue
        if text.startswith("Answer"):
            has_answer_line = True
            parts.append(("space", None, 32))
            text = "Answer ________ " + text.removeprefix("Answer").strip()
        elif (
            not choice
            and question in RESTORED_STEMS
            and not text.startswith("This question")
        ):
            if restored:
                continue
            text = RESTORED_STEMS[question]
            restored = True
        elif question == 40:
            text = re.sub(r"length of\s+foot", "length of 1/2 foot", text)
        size = 9 if choice else 9.2
        parts.extend(("text", line, size) for line in wrap(text, 252, size, font))
    if question >= 36 and not has_answer_line:
        parts.append(
            ("response_lines", None, 39)
            if question in (41, 42, 43)
            else ("space", None, 27)
        )
    return parts


def height(part):
    kind, value, size = part
    if kind == "figure":
        return value.height * size + 10
    return 11.5 if kind == "text" else size


def render_grade5_student(source_path, manifest, destination):
    """Render atomic question blocks with figure and formula vector crops."""
    source_bytes = Path(source_path).read_bytes()
    if (
        sha256(source_bytes).hexdigest() != SOURCE_SHA256
        or manifest["source_sha256"] != SOURCE_SHA256
    ):
        raise ValueError("Source PDF hash does not match the approved transcription")
    font = pymupdf.Font("helv")
    regions = manifest["regions"]
    selection = [1, 2, 3, 4, 7, 9, 10, 12, 15, 16, 19, 27, 28, *range(30, 45)]
    if [region["id"] for region in regions] != selection:
        raise ValueError("Region sequence does not match the historical selection")
    maximum_pages = manifest.get("maximum_pages", 4)
    if type(maximum_pages) is not int or not 1 <= maximum_pages <= 4:
        raise ValueError("The historical Grade 5 profile permits at most four pages")
    with pymupdf.open(
        stream=source_bytes, filetype="pdf"
    ) as source, pymupdf.open() as book:
        column = 1
        y = 760
        placement = []
        for region in regions:
            source_index = region["source_page"] - 1
            parts = extract(source[source_index], region, font)
            block_height = sum(map(height, parts)) + 6
            if block_height > 690:
                raise ValueError(f"Question {region['id']} exceeds an empty column")
            if y + block_height > 754:
                if column == 0:
                    column = 1
                else:
                    if len(book) >= maximum_pages:
                        raise ValueError(
                            f"Student worksheet exceeds {maximum_pages} pages"
                        )
                    page = book.new_page(width=612, height=792)
                    page.insert_text(
                        (30, 30), "MTS | " + manifest["title"], fontsize=12
                    )
                    page.insert_text(
                        (30, 49),
                        "Name: __________________________  Date: ______________",
                        fontsize=9,
                    )
                    column = 0
                y = 64
            x = 30 if column == 0 else 316
            placement.append(
                dict(
                    id=region["id"],
                    page=len(book),
                    column=column + 1,
                    y=y,
                    height=block_height,
                )
            )
            for part in parts:
                kind, value, size = part
                if kind == "text":
                    page.insert_text(
                        (x, y + size), value.replace("−", "-"), fontsize=size
                    )
                elif kind == "figure":
                    inset = 5
                    target = pymupdf.Rect(
                        x,
                        y + inset,
                        x + value.width * size,
                        y + inset + value.height * size,
                    )
                    page.show_pdf_page(target, source, source_index, clip=value)
                elif kind == "response_lines":
                    for offset in (12, 24, 36):
                        page.draw_line(
                            (x, y + offset), (x + 250, y + offset), width=0.4
                        )
                y += height(part)
            y += 6
        for index, rendered_page in enumerate(book, 1):
            rendered_page.insert_text((548, 776), f"{index} / {len(book)}", fontsize=8)
        book.save(destination, garbage=4, deflate=True)
    return placement
