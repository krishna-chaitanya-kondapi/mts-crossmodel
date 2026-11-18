"""Completed reviews must never survive changed inputs, images or evidence."""

from hashlib import sha256
import json
from pathlib import Path
import sys

import pymupdf
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))
from mts.products.mock_assessment.review_catalog import (
    match_frozen_review,
    page_fingerprints,
    manifest_fingerprint,
)


@pytest.fixture
def frozen_case(tmp_path):
    fixtures = tmp_path / "specs" / "generate_mock_assessment" / "fixtures"
    fixtures.mkdir(parents=True)
    student = tmp_path / "student.pdf"
    teacher = tmp_path / "teacher.pdf"
    for file in [student, teacher]:
        with pymupdf.open() as pdf:
            p = pdf.new_page()
            p.insert_text((40, 40), "Reviewed content")
            pdf.save(file)
    evidence = tmp_path / "academic.md"
    evidence.write_bytes(b"Reviewed independent reasoning and source comparison.")
    kwargs = {
        "source_sha256": "source-fingerprint",
        "student_manifest_sha256": manifest_fingerprint({"question": "verified"}),
        "teacher_manifest_sha256": manifest_fingerprint({"answer": "verified"}),
        "implementation_hashes": {"renderer.py": "code-fingerprint"},
        "student": student,
        "teacher": teacher,
    }
    entry = {
        key: value for key, value in kwargs.items() if key not in {"student", "teacher"}
    }
    entry.update(
        {
            "renderer_version": pymupdf.VersionBind,
            "student_page_pixels": page_fingerprints(student),
            "teacher_page_pixels": page_fingerprints(teacher),
            "academic_review": "PASS",
            "source_fidelity": "PASS",
            "visual_review": "PASS",
            "evidence": [
                {
                    "path": "academic.md",
                    "sha256": sha256(evidence.read_bytes()).hexdigest(),
                }
            ],
        }
    )
    catalog = fixtures.parent / "verified-profiles.json"
    catalog.write_text(json.dumps({"profiles": {"example": entry}}))
    return fixtures, kwargs, evidence, catalog


def test_identical_reviewed_content_transfers_quality_status(frozen_case):
    fixtures, kwargs, _, _ = frozen_case
    result = match_frozen_review("example", fixtures, **kwargs)
    assert all(
        result[field] == "PASS"
        for field in ["academic_review", "source_fidelity", "visual_review"]
    )


@pytest.mark.parametrize(
    "field", ["source_sha256", "student_manifest_sha256", "teacher_manifest_sha256"]
)
def test_changed_input_requires_new_review(frozen_case, field):
    fixtures, kwargs, _, _ = frozen_case
    kwargs[field] = "changed"
    assert (
        match_frozen_review("example", fixtures, **kwargs)["academic_review"]
        == "NOT_VERIFIED"
    )


def test_changed_evidence_requires_new_review(frozen_case):
    fixtures, kwargs, evidence, _ = frozen_case
    evidence.write_bytes(b"Changed review content")
    assert (
        match_frozen_review("example", fixtures, **kwargs)["source_fidelity"]
        == "NOT_VERIFIED"
    )


def test_changed_rendered_page_requires_new_review(frozen_case):
    fixtures, kwargs, _, _ = frozen_case
    replacement = kwargs["student"].with_name("changed.pdf")
    with pymupdf.open() as pdf:
        page = pdf.new_page()
        page.insert_text((40, 40), "An unreviewed change")
        pdf.save(replacement)
    kwargs["student"] = replacement
    assert (
        match_frozen_review("example", fixtures, **kwargs)["visual_review"]
        == "NOT_VERIFIED"
    )


def test_missing_catalog_is_never_pass(frozen_case):
    fixtures, kwargs, _, catalog = frozen_case
    catalog.unlink()
    assert (
        match_frozen_review("example", fixtures, **kwargs)["academic_review"]
        == "NOT_VERIFIED"
    )


def test_manifest_fingerprint_ignores_json_serialization_only():
    left = json.loads('{"question": "same", "points": 2}')
    right = json.loads('{\n  "points":2,\n  "question":"same"\n}')
    assert manifest_fingerprint(left) == manifest_fingerprint(right)
    assert manifest_fingerprint(left) != manifest_fingerprint(
        {"question": "different", "points": 2}
    )
