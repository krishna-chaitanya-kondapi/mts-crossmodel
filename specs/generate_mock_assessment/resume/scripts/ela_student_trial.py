"""Four-page ELA layout trial using NYSED questions and a historical passage transcript."""
import json
from pathlib import Path
import re
import sys
import unicodedata

import pymupdf as pdf

sys.path.insert(0, str(Path("work/mts-crossmodel/src").resolve()))
from mts.products.mock_assessment.grade5_student import wrap

FONT = pdf.Font("helv")
ROOT = Path("work/golden")
SOURCE = ROOT / "NY_ELA_Grade6_2025_Released_Test_Questions.pdf"
GOLDEN = ROOT / "MTS-ELA-RC-6thGrade-WeeklyWorksheet-2026-09-28.pdf"
NORMALIZE = str.maketrans({"\ue062": "Th", "\ue09d": "ft"})


def clean(text):
    value = unicodedata.normalize("NFKC", text.translate(NORMALIZE))
    return " ".join(value.translate(str.maketrans({"“": '"', "”": '"', "‘": "'", "’": "'", "—": "-", "–": "-"})).split())


def write_column(page, blocks, x, y, width=250, size=9.6, gap=5):
    for text in blocks:
        for line in wrap(text, width, size, FONT):
            if y > 747:
                raise ValueError(f"Text overflows page {page.number + 1}")
            page.insert_text((x, y), line, fontsize=size)
            y += size + 2
        y += gap
    return y


def passage_blocks(page):
    columns = [[], []]
    for x, y, _, _, text, *_ in page.get_text("blocks"):
        if y < (145 if page.number == 0 else 109) or y > 720:
            continue
        index = int(x >= 300)
        paragraph = clean(text)
        if page.number == 0 and paragraph.startswith("4 "):
            columns[index].append("The Purple Solution")
        if page.number == 0 and paragraph.startswith("11 "):
            columns[index].append("Making Magic")
        if page.number == 2 and paragraph.startswith("5 "):
            columns[index].append("Rochester, New York's Lilac Festival: A Local Legacy")
        if page.number == 2 and paragraph.startswith("10 "):
            columns[index].append("Immigrant Life in New York: A Local Legacy")
        if paragraph.startswith("10 ") and page.number == 0:
            paragraph = paragraph.removesuffix(" Making Magic")
        if page.number == 2:
            paragraph = paragraph.removesuffix(" Rochester, New York\x27s Lilac Festival: A Local Legacy")
            paragraph = paragraph.removesuffix(" Immigrant Life in New York: A Local Legacy")
        columns[index].append(paragraph)
    return columns


def questions(source, page_numbers):
    result = []
    for number in page_numbers:
        page = source[number - 1]
        blocks = page.get_text("blocks")
        anchors = sorted((b[1] - 12, int(b[4].strip())) for b in blocks
                         if b[0] < 72 and b[4].strip().isdigit())
        for i, (start, question) in enumerate(anchors):
            end = anchors[i + 1][0] if i + 1 < len(anchors) else 690
            text = []
            parts = sorted((b for b in blocks if b[0] >= 70 and start <= b[1] < end), key=lambda b: (b[1], b[0]))
            for b in parts:
                value = clean(b[4])
                if re.fullmatch(r"[A-D]", value) and text and not text[-1].startswith("Choice "):
                    previous = text.pop()
                    text.append(f"{value}. {previous}")
                else:
                    text.append(value)
            result.append((question, text))
    return result


def add_questions(page, rows, start_number, y, x):
    for offset, (original, blocks) in enumerate(rows):
        y = write_column(page, [f"{start_number + offset}. {blocks[0]}", *blocks[1:]], x, y, size=9.1, gap=1)
        y += 9
    return y


with pdf.open(SOURCE) as source, pdf.open(GOLDEN) as golden, pdf.open() as output:
    for group, (golden_index, source_pages, first_number, title, author) in enumerate((
        (0, [12,13,14], 1, "Cracking Code Purple", "Anna Ouchchy"),
        (2, [18,19,20,21], 8, "Excerpt from New York: Local Legacies", "Library of Congress"),
    ), 1):
        passage = output.new_page(width=612, height=792)
        passage.insert_text((38, 42), f"Passage {group} | {title}", fontsize=15)
        passage.insert_text((38, 59), f"By {author}", fontsize=10)
        start = 85
        if group == 2:
            context = [clean(b[4]) for b in golden[golden_index].get_text("blocks") if 81 <= b[1] <= 101]
            start = write_column(passage, [" ".join(context)], 38, start, 530)
        cols = passage_blocks(golden[golden_index])
        for idx, blocks in enumerate(cols):
            write_column(passage, blocks, 38 if idx == 0 else 318, start)
        questions_page = output.new_page(width=612, height=792)
        questions_page.insert_text((38, 38), f"Passage {group} | Questions", fontsize=13)
        rows = questions(source, source_pages)
        expected = list(range(8, 15)) if group == 1 else list(range(22, 29))
        assert [n for n, _ in rows] == expected
        if group == 1:
            clip = pdf.Rect(162, 293, 452, 562)
            questions_page.show_pdf_page(pdf.Rect(222, 46, 390, 202), source, 9, clip=clip)
            add_questions(questions_page, rows[:4], 1, 224, 38)
            add_questions(questions_page, rows[4:], 5, 224, 318)
        else:
            bottom = max(add_questions(questions_page, rows[:3], 8, 65, 38),
                         add_questions(questions_page, rows[3:5], 11, 65, 318))
            for n, (_, blocks) in enumerate(rows[5:], 13):
                bottom = write_column(questions_page, [f"{n}. {blocks[0]}", *blocks[1:]], 38, bottom + 10, 532, 9.1)
                for i in range(5):
                    questions_page.draw_line((38, bottom + i * 13), (570, bottom + i * 13), width=0.4)
                bottom += 70
            assert bottom < 765
    output.save("work/ela-student-diagnostic.pdf", garbage=4, deflate=True)
    for i, page in enumerate(output, 1):
        page.get_pixmap(alpha=False).save(f"work/ela-student-{i}.png")
    print(len(output), "student pages")
