"""Failure and retry coverage for staged RunSpec execution."""

from copy import deepcopy
from hashlib import sha256
import importlib
import json
from pathlib import Path
import sys

import pymupdf
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))
runner = importlib.import_module("mts.products.mock_assessment.run_benchmark")
FIXTURES = (
    Path(__file__).resolve().parents[2] / "specs/generate_mock_assessment/fixtures"
)


@pytest.fixture
def local_run(tmp_path, monkeypatch):
    source_root = tmp_path / "source"
    source_root.mkdir()
    spec = json.loads((FIXTURES / "ny2024_math_grade5-runspec.json").read_text())
    source = source_root / spec["source_filename"]
    with pymupdf.open() as pdf:
        pdf.new_page()
        pdf.save(source)
    spec["source_sha256"] = sha256(source.read_bytes()).hexdigest()
    fixtures = tmp_path / "fixtures"
    fixtures.mkdir()
    for name in ["grade5-student-manifest.json", "grade5-teacher-manifest.json"]:
        manifest = json.loads((FIXTURES / name).read_text(encoding="utf-8-sig"))
        manifest["source_sha256"] = spec["source_sha256"]
        (fixtures / name).write_text(json.dumps(manifest))
    path = tmp_path / "runspec.json"
    path.write_text(json.dumps(spec))

    def student_renderer(source, manifest, destination):
        with pymupdf.open() as pdf:
            pdf.new_page(width=612, height=792)
            pdf.save(destination)
        return [{"id": row["id"]} for row in manifest["regions"]]

    monkeypatch.setattr(runner, "render_grade5_student", student_renderer)
    return path, source_root, tmp_path / "output", fixtures


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("run_id", "../escape"),
        ("execution", "production"),
        ("instructional_monday", "2026-09-29"),
        ("estimated_runtime_seconds", float("nan")),
        ("profile", "unknown"),
    ],
)
def test_invalid_runspec_is_rejected(field, value):
    spec = json.loads((FIXTURES / "ny2024_math_grade5-runspec.json").read_text())
    spec[field] = value
    with pytest.raises(ValueError):
        runner.validate_runspec(spec)


def test_completed_identity_is_preserved_on_retry(local_run):
    path, source, output, fixtures = local_run
    first = runner.run_benchmark(path, source, output, fixtures)
    files = {
        p.relative_to(output): p.read_bytes() for p in output.rglob("*") if p.is_file()
    }
    with pytest.raises(FileExistsError):
        runner.run_benchmark(path, source, output, fixtures)
    assert files == {
        p.relative_to(output): p.read_bytes() for p in output.rglob("*") if p.is_file()
    }
    assert first["production_publications"] == 0
    assert first["academic_review"] == "NOT_VERIFIED"


def test_partial_phase_move_rolls_back_and_can_be_retried(local_run, monkeypatch):
    path, source, output, fixtures = local_run
    rename = runner.os.rename
    calls = 0

    def fail_second_move(before, after):
        nonlocal calls
        calls += 1
        if calls == 2:
            raise OSError("injected filesystem failure")
        return rename(before, after)

    monkeypatch.setattr(runner.os, "rename", fail_second_move)
    with pytest.raises(OSError, match="injected"):
        runner.run_benchmark(path, source, output, fixtures)
    assert not list(output.rglob("*.pdf"))
    assert not list(output.glob("*.lock"))
    monkeypatch.setattr(runner.os, "rename", rename)
    assert (
        runner.run_benchmark(path, source, output, fixtures)["status"]
        == "REVIEW_REQUIRED"
    )


def test_concurrent_run_identity_is_locked(local_run):
    path, source, output, fixtures = local_run
    output.mkdir()
    spec = json.loads(path.read_text())
    lock = output / f'.{spec["run_id"]}.lock'
    lock.write_text("another run")
    with pytest.raises(FileExistsError):
        runner.run_benchmark(path, source, output, fixtures)
    assert lock.read_text() == "another run"
