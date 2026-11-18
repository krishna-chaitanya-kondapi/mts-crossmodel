"""Approval boundaries and preservation of other approved publication files."""

from hashlib import sha256
import importlib
import json
from pathlib import Path
import sys

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))
from mts.products.mock_assessment.release import publish_approved_assessment

neutral = importlib.import_module("mts.publishing.coordinated_release")


@pytest.fixture
def approved_run(tmp_path):
    run_id = "mock-verified"
    day = "2026-09-28"
    run = tmp_path / "run"
    files = run / "02-Run" / day / run_id
    files.mkdir(parents=True)
    artifacts = {}
    for name in ("student.pdf", "teacher.pdf"):
        (files / name).write_bytes(b"%PDF review " + name.encode())
        artifacts[name] = sha256((files / name).read_bytes()).hexdigest()
    post = run / "03-PostRun" / day / run_id
    post.mkdir(parents=True)
    (post / "runlog.json").write_text(
        json.dumps(
            {
                "run_id": run_id,
                "execution_revision": "verified-revision",
                "artifacts": artifacts,
            }
        )
    )
    review = {
        "status": "PASS",
        "academic_review": "PASS",
        "source_fidelity": "PASS",
        "visual_review": "PASS",
        "structural_checks": "PASS",
        "run_id": run_id,
        "execution_revision": "verified-revision",
        "artifacts": artifacts,
    }
    approval = {
        "kind": "human_final_release",
        "approved": True,
        "approved_by": "Test reviewer",
        "approved_at": "2026-11-18T12:00:00-05:00",
        "run_id": run_id,
        "artifacts": artifacts,
    }
    gate = {
        "status": "READY_FOR_ACCEPTANCE",
        "pending_mandatory": [],
        "revision": "verified-revision",
    }
    destination = tmp_path / "PrintReady"
    return run, review, approval, gate, destination


def test_missing_final_approval_blocks_all_writes(approved_run):
    run, review, _, gate, destination = approved_run
    with pytest.raises(ValueError, match="human approval"):
        publish_approved_assessment(run, review, {}, gate, destination)
    assert not destination.exists()


def test_incomplete_development_gate_blocks_publication(approved_run):
    run, review, approval, gate, destination = approved_run
    gate["status"] = "NOT_DONE"
    with pytest.raises(ValueError, match="mandatory"):
        publish_approved_assessment(run, review, approval, gate, destination)
    assert not destination.exists()


def test_artifact_change_after_approval_is_rejected(approved_run):
    run, review, approval, gate, destination = approved_run
    next(run.rglob("student.pdf")).write_bytes(b"changed")
    with pytest.raises(ValueError, match="changed"):
        publish_approved_assessment(run, review, approval, gate, destination)
    assert not destination.exists()


def test_other_subject_and_weekly_files_are_preserved(approved_run):
    run, review, approval, gate, destination = approved_run
    destination.mkdir()
    weekly = destination / "MTS-Math-Weekly-student.pdf"
    other = destination / "MTS-ELA-Weekly-key.pdf"
    weekly.write_bytes(b"approved weekly")
    other.write_bytes(b"approved other subject")
    result = publish_approved_assessment(run, review, approval, gate, destination)
    assert weekly.read_bytes() == b"approved weekly"
    assert other.read_bytes() == b"approved other subject"
    assert len(result["published"]) == 2
    assert len(result["preserved"]) == 2


def test_replacement_needs_the_existing_file_fingerprint(approved_run):
    run, review, approval, gate, destination = approved_run
    destination.mkdir()
    old = destination / "mock-verified-student.pdf"
    old.write_bytes(b"earlier approved version")
    with pytest.raises(ValueError, match="prior fingerprint"):
        publish_approved_assessment(run, review, approval, gate, destination)
    assert old.read_bytes() == b"earlier approved version"


def test_mid_publication_failure_restores_prior_set(approved_run, monkeypatch):
    run, review, approval, gate, destination = approved_run
    destination.mkdir()
    prior = destination / "mock-verified-student.pdf"
    prior.write_bytes(b"prior approved version")
    approval["replace_hashes"] = {prior.name: sha256(prior.read_bytes()).hexdigest()}
    real_replace = neutral.os.replace
    calls = 0

    def fail_second_move(before, after):
        nonlocal calls
        calls += 1
        if calls == 2:
            raise OSError("injected publication failure")
        return real_replace(before, after)

    monkeypatch.setattr(neutral.os, "replace", fail_second_move)
    with pytest.raises(OSError, match="injected"):
        publish_approved_assessment(run, review, approval, gate, destination)
    assert prior.read_bytes() == b"prior approved version"
    assert not (destination / "mock-verified-teacher.pdf").exists()
    assert not (destination / ".mts-publication.lock").exists()


def test_failed_local_rollback_retains_approved_backup(approved_run, monkeypatch):
    run, review, approval, gate, destination = approved_run
    destination.mkdir()
    prior = destination / "mock-verified-student.pdf"
    prior.write_bytes(b"prior approved version")
    approval["replace_hashes"] = {prior.name: sha256(prior.read_bytes()).hexdigest()}
    real_replace = neutral.os.replace
    calls = 0

    def persistent_failure(before, after):
        nonlocal calls
        calls += 1
        if calls >= 2:
            raise OSError("persistent destination failure")
        return real_replace(before, after)

    monkeypatch.setattr(neutral.os, "replace", persistent_failure)
    with pytest.raises(RuntimeError, match="backups retained"):
        publish_approved_assessment(run, review, approval, gate, destination)
    backups = list(destination.glob(".release-*/*.previous"))
    assert len(backups) == 1
    assert backups[0].read_bytes() == b"prior approved version"
    assert not (destination / "mock-verified-teacher.pdf").exists()
    assert not (destination / ".mts-publication.lock").exists()
