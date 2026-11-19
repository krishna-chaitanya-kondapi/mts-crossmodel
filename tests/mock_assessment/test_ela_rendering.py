import hashlib
import json
import re
import subprocess
import sys
from collections import Counter
from pathlib import Path

import pymupdf
import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

from mts.products.mock_assessment.ela_teacher import render_ela_teacher


def test_ela_teacher_retains_answers_and_avoids_punctuation_fallback(tmp_path):
    manifest_path = ROOT / "specs/generate_mock_assessment/fixtures/ela-teacher-manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8-sig"))
    output = tmp_path / "teacher.pdf"

    render_ela_teacher(manifest, output)

    with pymupdf.open(output) as document:
        assert len(document) == 2
        text = "\n".join(page.get_text() for page in document)
    answers = [line.split(":", 1)[1].strip() for line in text.splitlines()
               if line.startswith("Correct Answer:")]
    assert answers == manifest["official_answers"]
    assert "MTS ELA MOCK TEST" in text
    assert "\u00b7" not in text
    assert "\ufffd" not in text
    expected_words = Counter(re.findall(r"\w+", " ".join(manifest["pages"]).translate(
        str.maketrans({
            "\u2018": "'", "\u2019": "'", "\u201c": '"', "\u201d": '"',
            "\u2013": "-", "\u2014": "-", "\u2022": "|",
        })
    )))
    actual_words = Counter(re.findall(r"\w+", text))
    assert all(actual_words[word] >= count for word, count in expected_words.items())


@pytest.mark.parametrize("valid_hash", [True, False], ids=["matching-source", "wrong-source"])
def test_ela_student_cli_uses_hash_bound_region_renderer(tmp_path, valid_hash):
    source_path = tmp_path / "source.pdf"
    with pymupdf.open() as source:
        page = source.new_page(width=612, height=792)
        page.insert_text((40, 50), "Source item", fontsize=12)
        source.save(source_path)
    source_hash = hashlib.sha256(source_path.read_bytes()).hexdigest()
    manifest_path = tmp_path / "manifest.json"
    manifest_path.write_text(json.dumps({
        "title": "ELA student review",
        "source_sha256": source_hash if valid_hash else "0" * 64,
        "scale": 0.75,
        "maximum_pages": 1,
        "regions": [{"id": 8, "source_page": 1, "bounds": [30, 30, 180, 70]}],
    }), encoding="utf-8")
    output_path = tmp_path / "student.pdf"
    placements_path = tmp_path / "placements.json"

    result = subprocess.run([
        sys.executable, str(ROOT / "scripts/generate_mock_assessment.py"),
        "ela-student", "--source", str(source_path), "--manifest", str(manifest_path),
        "--output", str(output_path), "--placements", str(placements_path),
    ], cwd=tmp_path, capture_output=True, text=True)

    if not valid_hash:
        assert result.returncode != 0
        assert "Source PDF hash does not match" in result.stderr
        assert not output_path.exists()
        assert not placements_path.exists()
        return

    assert result.returncode == 0, result.stderr
    with pymupdf.open(output_path) as document:
        assert len(document) == 1
        assert "Source item" in document[0].get_text()
    assert json.loads(placements_path.read_text(encoding="utf-8")) == {
        "placements": [{"id": 8, "page": 1, "bounds": [36, 64, 148.5, 94], "scale": 0.75}],
    }
