import hashlib
import hmac
import json
import secrets
import subprocess
import sys
from pathlib import Path

import pymupdf
import pytest

from mts.products.mock_assessment.approval import render_approved_student

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
        page = pdf.new_page()
        page.insert_text((36, 36), "First synthetic selection")
        page.insert_text((36, 90), "Excluded synthetic text")
        page.insert_text((36, 150), "Second synthetic selection")
        pdf.save(source)
    draft = {
        "run": {"worksheet_type": "mock_assessment", "subject": "ela", "grade": 6},
        "assessment": {"purpose": "benchmark", "length": "mini"},
        "source": {
            "mode": "source_based",
            "rights_basis": "Original synthetic test fixture created by this test.",
            "sha256": hashlib.sha256(source.read_bytes()).hexdigest(),
            "selection": [
                {"source_number": 8, "source_page": 1, "type": "multiple_choice", "bounds": [28.1, 15.1, 224.9, 49.9]},
                {"source_number": 9, "source_page": 1, "type": "constructed_response", "bounds": [28, 130, 225, 165]},
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

    key = secrets.token_bytes(32)

    def sign(record):
        message = json.dumps(record, sort_keys=True, separators=(",", ":")).encode("ascii")
        return {**record, "hmac_sha256": hmac.new(key, b"mts/mock-assessment/pre-run/v1\0" + message, "sha256").hexdigest()}

    signed = sign(approval)
    for decision, decision_key, error in (
        (approval, key, "authentication failed"),
        ({**signed, "reviewer": "Changed reviewer"}, key, "authentication failed"),
        (signed, secrets.token_bytes(32), "authentication failed"),
        (signed, b"", "trusted approval key"),
        (sign({**approval, "scope": "RELEASE"}), key, "separate pre-run approval"),
    ):
        with pytest.raises(ValueError, match=error):
            render_approved_student(bundle, source, decision, output, approval_key=decision_key)
    for name in before:
        path = bundle / name
        path.write_bytes(before[name] + b"\n")
        with pytest.raises(ValueError, match="does not match"):
            render_approved_student(bundle, source, signed, output, approval_key=key)
        path.write_bytes(before[name])
    assert not output.exists()

    render_approved_student(bundle, source, signed, output, approval_key=key)
    with pymupdf.open(output) as pdf, pymupdf.open(source) as original:
        page = pdf[0]
        assert not page.get_xobjects()
        assert "synthetic selection" not in page.get_text()
        images = sorted(page.get_image_info(xrefs=True), key=lambda image: image["bbox"][1])
        assert len(images) == 2
        clips = [(28.25, 15.25, 224.75, 49.75), (28, 130, 225, 165)]
        for image, clip in zip(images, clips, strict=True):
            expected = original[0].get_pixmap(dpi=288, clip=pymupdf.Rect(clip), annots=False)
            embedded = pymupdf.Pixmap(pdf, image["xref"])
            assert (embedded.width, embedded.height, embedded.samples) == (
                expected.width, expected.height, expected.samples,
            )
    before_output = output.read_bytes()
    with pytest.raises(FileExistsError):
        render_approved_student(bundle, source, signed, output, approval_key=key)
    assert output.read_bytes() == before_output
