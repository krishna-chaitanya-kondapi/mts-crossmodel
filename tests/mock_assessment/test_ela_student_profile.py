"""Regression tests for source-bound ELA composition without a golden PDF dependency."""

from copy import deepcopy
from hashlib import sha256
import json
from pathlib import Path
import sys

import pymupdf
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))
from mts.products.mock_assessment.ela_student import render_ela_student


@pytest.fixture
def historical_profile(tmp_path):
    source = tmp_path / "official.pdf"
    with pymupdf.open() as pdf:
        for number in range(1, 22):
            page = pdf.new_page(width=612, height=792)
            page.insert_text((180, 320), f"Source figure {number}")
        pdf.save(source)
    manifest = json.loads(
        (
            Path(__file__).resolve().parents[2]
            / "specs/generate_mock_assessment/fixtures/ela-student-manifest.json"
        ).read_text()
    )
    manifest["source_sha256"] = sha256(source.read_bytes()).hexdigest()
    for index, passage in enumerate(manifest["passages"]):
        passage["paragraphs"] = {
            str(n): f"Source paragraph {n}." for n in range(1, 13 - index)
        }
    return source, manifest


def test_source_profile_renders_four_pages_and_all_response_lines(
    historical_profile, tmp_path
):
    source, manifest = historical_profile
    output = tmp_path / "student.pdf"
    placements = render_ela_student(source, manifest, output)
    assert [row["number"] for row in placements] == list(range(1, 15))
    with pymupdf.open(output) as pdf:
        assert len(pdf) == 4
        assert all(tuple(page.rect) == (0, 0, 612, 792) for page in pdf)
        assert "Source figure 10" in pdf[1].get_text()
        rules = [d for d in pdf[3].get_drawings() if d["rect"].width == 532]
        assert len(rules) == 10
        assert "14." in pdf[3].get_text()


def test_source_profile_rejects_changed_source(historical_profile, tmp_path):
    source, manifest = historical_profile
    manifest["source_sha256"] = "0" * 64
    with pytest.raises(ValueError, match="hash mismatch"):
        render_ela_student(source, manifest, tmp_path / "student.pdf")


def test_source_profile_rejects_missing_paragraph(historical_profile, tmp_path):
    source, manifest = historical_profile
    del manifest["passages"][0]["paragraphs"]["8"]
    with pytest.raises(ValueError, match="Incomplete"):
        render_ela_student(source, manifest, tmp_path / "student.pdf")


def test_source_profile_rejects_changed_question_order(historical_profile, tmp_path):
    source, manifest = historical_profile
    manifest["questions"][0], manifest["questions"][1] = (
        manifest["questions"][1],
        manifest["questions"][0],
    )
    with pytest.raises(ValueError, match="historical selection"):
        render_ela_student(source, manifest, tmp_path / "student.pdf")
