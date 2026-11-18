import hashlib
import json
import sys
from pathlib import Path

import pytest
import pymupdf

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

from mts.products.mock_assessment import grade4_student
from mts.products.mock_assessment.grade4_student import (
    RESPONSE_RULES,
    SOURCE_EXPRESSIONS,
    _insert_page_heading,
    _validated_page_breaks,
    choices_and_text,
    render_grade4_student,
)


def test_accepts_breaks_for_selected_items():
    assert _validated_page_breaks([36, 41], [36, 37, 40, 41, 42]) == [36, 41]
    assert _validated_page_breaks([43], [41, 42, 43, 44]) == [43]


def test_first_page_heading_includes_student_name_and_date_fields():
    with pymupdf.open() as document:
        page = document.new_page(width=612, height=792)
        _insert_page_heading(page, "Grade 4 Mathematics", include_student_fields=True)
        text = page.get_text()

    assert "Grade 4 Mathematics" in text
    assert "Name:" in text
    assert "Date:" in text


def test_interior_page_heading_can_be_omitted():
    with pymupdf.open() as document:
        page = document.new_page(width=612, height=792)
        _insert_page_heading(page, "Grade 4 Mathematics", include_title=False)
        text = page.get_text()

    assert text == ""


@pytest.mark.parametrize(
    ("question", "prompt", "inline_fraction", "bounds", "y"),
    [
        (2, "What value makes the equation shown below true?", "3/4", [70, 250, 550, 450], 260),
        (22, "What is the value of the expression shown below?", "4 1/4", [70, 350, 550, 600], 370),
    ],
)
def test_stacked_fraction_stems_use_source_crops(question, prompt, inline_fraction, bounds, y):
    with pymupdf.open() as document:
        page = document.new_page(width=612, height=792)
        page.insert_text((75, y), prompt, fontsize=9.2)
        parts = choices_and_text(
            page,
            {"id": question, "bounds": bounds},
            pymupdf.Font("helv"),
        )

    text = " ".join(value for kind, value, _ in parts if kind == "text")
    crops = [(value, scale) for kind, value, scale in parts if kind == "crop"]
    assert inline_fraction not in text
    assert crops == [SOURCE_EXPRESSIONS[question]]


def test_configured_column_break_preserves_grade4_page_four_grouping(tmp_path, monkeypatch):
    source_path = tmp_path / "source.pdf"
    with pymupdf.open() as source:
        for _ in range(32):
            source.new_page(width=612, height=792)
        source.save(source_path)

    manifest_path = ROOT / "specs/generate_mock_assessment/fixtures/grade4-student-manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8-sig"))
    source_hash = hashlib.sha256(source_path.read_bytes()).hexdigest()
    manifest["source_sha256"] = source_hash
    monkeypatch.setattr(grade4_student, "SOURCE_SHA256", source_hash)

    placements = render_grade4_student(source_path, manifest, tmp_path / "student.pdf")
    by_item = {placement["item"]: placement for placement in placements}

    assert [(by_item[item]["page"], by_item[item]["column"]) for item in (41, 42, 43, 44)] == [
        (4, 1),
        (4, 1),
        (4, 2),
        (4, 2),
    ]
    with pymupdf.open(tmp_path / "student.pdf") as rendered:
        line_count = sum(
            1
            for page in rendered
            for drawing in page.get_drawings()
            if 251 <= drawing["rect"].width <= 253 and drawing["rect"].height < 1
        )
    assert line_count == sum(RESPONSE_RULES.values())


@pytest.mark.parametrize("value", [None, "42", [True], [[42]], [99], [42, 42]])
def test_rejects_invalid_page_breaks(value):
    with pytest.raises(ValueError, match="unique selected item IDs"):
        _validated_page_breaks(value, [41, 42, 43])
