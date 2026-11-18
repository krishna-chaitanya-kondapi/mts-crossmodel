"""Render the source-derived historical Grade 6 ELA selection."""

from hashlib import sha256
from pathlib import Path

import pymupdf

from .ela_teacher import _wrap


def render_ela_student(source_path, manifest, destination):
    source_bytes = Path(source_path).read_bytes()
    if sha256(source_bytes).hexdigest() != manifest["source_sha256"]:
        raise ValueError("ELA source hash mismatch")
    passages = manifest["passages"]
    questions = manifest["questions"]
    if len(passages) != 2 or [q["source_number"] for q in questions] != [
        *range(8, 15),
        *range(22, 29),
    ]:
        raise ValueError("Invalid ELA historical selection")
    if [q["output_number"] for q in questions] != list(range(1, 15)):
        raise ValueError("Invalid ELA worksheet numbering")
    for passage, count in zip(passages, (12, 11)):
        if set(passage["paragraphs"]) != {str(n) for n in range(1, count + 1)}:
            raise ValueError("Incomplete ELA passage")
    font = pymupdf.Font("helv")
    placements = []

    def write(page, blocks, x, y, width=250, size=9.6, gap=5):
        for text in blocks:
            for line in _wrap(text, width, font, size):
                if y > 747:
                    raise ValueError("ELA content exceeds its page")
                page.insert_text((x, y), line, fontsize=size)
                y += size + 2
            y += gap
        return y

    def write_questions(page, rows, x, y):
        for question in rows:
            y0 = y
            y = (
                write(
                    page,
                    [
                        f'{question["output_number"]}. {question["blocks"][0]}',
                        *question["blocks"][1:],
                    ],
                    x,
                    y,
                    size=9.1,
                    gap=1,
                )
                + 9
            )
            placements.append(
                {
                    "number": question["output_number"],
                    "source_number": question["source_number"],
                    "page": page.number + 1,
                    "top": y0,
                    "bottom": y,
                }
            )
        return y

    with pymupdf.open(
        stream=source_bytes, filetype="pdf"
    ) as source, pymupdf.open() as output:
        for index, passage in enumerate(passages):
            page = output.new_page(width=612, height=792)
            page.insert_text(
                (38, 42), f'Passage {index+1} | {passage["title"]}', fontsize=14
            )
            page.insert_text((38, 59), f'By {passage["author"]}', fontsize=10)
            start = 85
            if passage.get("context"):
                start = write(page, [passage["context"]], 38, start, 530)
            columns = [[], []]
            for number, text in sorted(
                passage["paragraphs"].items(), key=lambda pair: int(pair[0])
            ):
                column = int(int(number) >= passage["split_before"])
                if number in passage["headings"]:
                    columns[column].append(passage["headings"][number])
                columns[column].append(f"{number} {text}")
            for col, blocks in enumerate(columns):
                write(page, blocks, 38 if col == 0 else 318, start)
            page = output.new_page(width=612, height=792)
            page.insert_text((38, 38), f"Passage {index+1} | Questions", fontsize=13)
            if index == 0:
                figure = manifest["cipher"]
                page.show_pdf_page(
                    pymupdf.Rect(222, 46, 390, 202),
                    source,
                    figure["source_page"] - 1,
                    clip=pymupdf.Rect(figure["bounds"]),
                )
                write_questions(page, questions[:4], 38, 224)
                write_questions(page, questions[4:7], 318, 224)
            else:
                y = max(
                    write_questions(page, questions[7:10], 38, 65),
                    write_questions(page, questions[10:12], 318, 65),
                )
                for question in questions[12:]:
                    top = y + 10
                    y = write(
                        page,
                        [
                            f'{question["output_number"]}. {question["blocks"][0]}',
                            *question["blocks"][1:],
                        ],
                        38,
                        top,
                        532,
                        9.1,
                    )
                    for line in range(5):
                        page.draw_line(
                            (38, y + line * 13), (570, y + line * 13), width=0.4
                        )
                    y += 70
                    if y >= 765:
                        raise ValueError("ELA constructed response exceeds page four")
                    placements.append(
                        {
                            "number": question["output_number"],
                            "source_number": question["source_number"],
                            "page": 4,
                            "top": top,
                            "bottom": y,
                        }
                    )
        output.save(destination, garbage=4, deflate=True)
    return placements
