import hashlib
import json
import subprocess
import sys
from pathlib import Path

import pymupdf
import pytest

from mts.products.mock_assessment.approval import run_approved_draft
from mts.products.mock_assessment.source_render import render_student

ROOT = Path(__file__).resolve().parents[2]


@pytest.mark.parametrize(("section", "field", "value", "error"), [
    (None, None, None, None),
    ("", "approval", True, "cannot contain status, approval, or release"),
    ("source", "rights_basis", "  ", "rights_basis"),
    ("source", "sha256", "0" * 64, "Source SHA-256 does not match"),
    ("blueprint", "constructed_response", 2, "format counts must sum"),
    ("presentation", "student_pagination", {"policy": "maximum", "pages": True}, "pages must be an integer"),
    ("source", "selection", [
        {"source_number": 8, "source_page": 2, "type": "multiple_choice"},
        {"source_number": 9, "source_page": 1, "type": "constructed_response"},
    ], "page exceeds the PDF page count"),
    ("source", "selection", [
        {"source_number": 8, "source_page": 1, "type": "multiple_choice"},
        {"source_number": 8, "source_page": 1, "type": "constructed_response"},
    ], "question numbers must be unique"),
    ("source", "selection", [
        {"source_number": 8, "source_page": 1, "type": "multiple_choice"},
        {"source_number": 9, "source_page": 1, "type": "multiple_choice"},
    ], "selection format counts must match"),
])
@pytest.mark.parametrize("emit_bundle", [False, True])
def test_draft_preflight_cli(tmp_path, section, field, value, error, emit_bundle):
    source = tmp_path / "source.pdf"
    with pymupdf.open() as pdf:
        pdf.new_page().insert_text((36, 36), "Original synthetic fixture")
        pdf.save(source)
    draft = {
        "run": {"worksheet_type": "mock_assessment", "subject": "ela", "grade": 6},
        "assessment": {"purpose": "benchmark", "length": "mini"},
        "source": {
            "mode": "source_based",
            "rights_basis": "Original synthetic test fixture created by this test.",
            "sha256": hashlib.sha256(source.read_bytes()).hexdigest(),
            "selection": [
                {"source_number": 8, "source_page": 1, "type": "multiple_choice"},
                {"source_number": 9, "source_page": 1, "type": "constructed_response"},
            ],
        },
        "blueprint": {"questions": 2, "multiple_choice": 1, "constructed_response": 1},
        "presentation": {
            "paper_size": "US_Letter",
            "orientation": "portrait",
            "student_pagination": {"policy": "maximum", "pages": 2},
        },
    }
    if section is not None:
        (draft[section] if section else draft)[field] = value
    runspec = tmp_path / "runspec.json"
    runspec.write_text(json.dumps(draft), encoding="utf-8")

    bundle = tmp_path / "review"
    command = [
        sys.executable, str(ROOT / "scripts" / "generate_mock_assessment.py"),
        "preflight", "--runspec", str(runspec), "--source", str(source),
    ]
    if emit_bundle:
        command.extend(["--review-dir", str(bundle)])
    result = subprocess.run(command, cwd=tmp_path, capture_output=True, text=True)

    if error is None:
        assert result.returncode == 0, result.stderr
        assert "rights and human approval not verified" in result.stdout
    else:
        assert result.returncode == 2, result.stderr
        assert error in result.stderr
    if error is not None or not emit_bundle:
        assert set(tmp_path.iterdir()) == {source, runspec}
        return

    record = json.loads((bundle / "runspec.json").read_text(encoding="utf-8"))
    assert record == {
        "status": "DRAFT",
        "rights_verified": False,
        "human_approval_verified": False,
        "runspec": draft,
    }
    with pymupdf.open(bundle / "runspec.pdf") as pdf:
        text = "".join(page.get_text() for page in pdf)
    assert "Draft, not approved" in text
    assert draft["source"]["sha256"] in text
    assert '"source_number": 9' in text
    before = {path.name: path.read_bytes() for path in bundle.iterdir()}
    retry = subprocess.run(command, cwd=tmp_path, capture_output=True, text=True)
    assert retry.returncode == 2, retry.stderr
    assert {path.name: path.read_bytes() for path in bundle.iterdir()} == before

    approval = {
        "decision": "APPROVED",
        "scope": "PRE_RUN",
        "reviewer": "Synthetic test reviewer",
        "runspec_json_sha256": hashlib.sha256(before["runspec.json"]).hexdigest(),
        "runspec_pdf_sha256": hashlib.sha256(before["runspec.pdf"]).hexdigest(),
    }
    output = tmp_path / "synthetic-student.pdf"

    def render(approved):
        assert approved == draft
        return render_student(source, {
            "title": "Synthetic approved-run fixture",
            "source_sha256": approved["source"]["sha256"],
            "scale": 0.75,
            "maximum_pages": 2,
            "regions": [{"id": 8, "source_page": 1, "bounds": [28, 15, 225, 50]}],
        }, output)

    for decision in ({}, {**approval, "scope": "RELEASE"}):
        with pytest.raises(ValueError, match="separate pre-run approval"):
            run_approved_draft(bundle, source, decision, render)
    for name in before:
        path = bundle / name
        path.write_bytes(before[name] + b"\n")
        with pytest.raises(ValueError, match="does not match"):
            run_approved_draft(bundle, source, approval, render)
        path.write_bytes(before[name])
    assert not output.exists()

    placements = run_approved_draft(bundle, source, approval, render)
    assert [placement["id"] for placement in placements] == [8]
    with pymupdf.open(output) as pdf:
        assert "Original synthetic fixture" in pdf[0].get_text()
