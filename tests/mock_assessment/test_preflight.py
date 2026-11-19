import hashlib
import json
import subprocess
import sys
from pathlib import Path

import pymupdf
import pytest

ROOT = Path(__file__).resolve().parents[2]


@pytest.mark.parametrize(("section", "field", "value", "error"), [
    (None, None, None, None),
    ("source", "rights_basis", "  ", "rights_basis"),
    ("source", "sha256", "0" * 64, "Source SHA-256 does not match"),
    ("blueprint", "constructed_response", 2, "format counts must sum"),
    ("presentation", "student_pagination", {"policy": "maximum", "pages": True}, "pages must be an integer"),
])
def test_draft_preflight_cli(tmp_path, section, field, value, error):
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
        },
        "blueprint": {"questions": 2, "multiple_choice": 1, "constructed_response": 1},
        "presentation": {
            "paper_size": "US_Letter",
            "orientation": "portrait",
            "student_pagination": {"policy": "maximum", "pages": 2},
        },
    }
    if section is not None:
        draft[section][field] = value
    runspec = tmp_path / "runspec.json"
    runspec.write_text(json.dumps(draft), encoding="utf-8")

    result = subprocess.run([
        sys.executable, str(ROOT / "scripts" / "generate_mock_assessment.py"),
        "preflight", "--runspec", str(runspec), "--source", str(source),
    ], cwd=tmp_path, capture_output=True, text=True)

    if error is None:
        assert result.returncode == 0, result.stderr
        assert "rights and human approval not verified" in result.stdout
    else:
        assert result.returncode == 2, result.stderr
        assert error in result.stderr
    assert set(tmp_path.iterdir()) == {source, runspec}
