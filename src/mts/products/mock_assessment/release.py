"""Approval checks for publishing exact, fully verified assessment artifacts."""

from datetime import datetime
from hashlib import sha256
import json
from pathlib import Path

from mts.publishing.coordinated_release import publish_verified_files
from mts.publishing.coordinated_drive_release import publish_verified_drive_files


def approved_release_files(run_root, review, approval, development_gate):
    """Require completed quality gates and human approval before local publication."""
    if development_gate.get("status") != "READY_FOR_ACCEPTANCE":
        raise ValueError(
            "All mandatory development criteria must pass before publication"
        )
    if development_gate.get("pending_mandatory"):
        raise ValueError("Development verification has pending criteria")
    if (
        not isinstance(approval, dict)
        or approval.get("kind") != "human_final_release"
        or approval.get("approved") is not True
    ):
        raise ValueError("Explicit final human approval is required")
    if (
        not isinstance(approval.get("approved_by"), str)
        or not approval["approved_by"].strip()
    ):
        raise ValueError("Approval must identify the human approver")
    moment = datetime.fromisoformat(approval["approved_at"])
    if moment.tzinfo is None:
        raise ValueError("Approval timestamp must include its timezone")
    if review.get("status") != "PASS" or any(
        review.get(name) != "PASS"
        for name in [
            "academic_review",
            "source_fidelity",
            "visual_review",
            "structural_checks",
        ]
    ):
        raise ValueError("All per-run quality checks must pass")
    root = Path(run_root)
    log_paths = list(root.glob("03-PostRun/*/*/runlog.json"))
    requested = approval.get("run_id")
    matches = []
    for path in log_paths:
        log = json.loads(path.read_text())
        if log["run_id"] == requested:
            matches.append((path, log))
    if len(matches) != 1:
        raise ValueError("Approval must identify exactly one run")
    log_path, log = matches[0]
    if review.get("run_id") != requested:
        raise ValueError("Quality review must identify the approved run")
    if review.get("execution_revision") != log["execution_revision"]:
        raise ValueError("Quality review belongs to another execution revision")
    if development_gate.get("revision") != log["execution_revision"]:
        raise ValueError(
            "Development verification belongs to another execution revision"
        )
    expected = {name: log["artifacts"][name] for name in ("student.pdf", "teacher.pdf")}
    if approval.get("artifacts") != expected or review.get("artifacts") != expected:
        raise ValueError("Approval and quality review must bind both exact PDFs")
    monday = log_path.parent.parent.name
    source_folder = root / "02-Run" / monday / requested
    files = {
        f"{requested}-{role}.pdf": source_folder / f"{role}.pdf"
        for role in ("student", "teacher")
    }
    hashes = {
        f"{requested}-{role}.pdf": expected[f"{role}.pdf"]
        for role in ("student", "teacher")
    }
    for name, path in files.items():
        if sha256(path.read_bytes()).hexdigest() != hashes[name]:
            raise ValueError("An artifact changed after approval")
    return files, hashes


def publish_approved_assessment(
    run_root, review, approval, development_gate, destination
):
    files, hashes = approved_release_files(run_root, review, approval, development_gate)
    return publish_verified_files(
        files,
        destination,
        expected_hashes=hashes,
        replace_hashes=approval.get("replace_hashes", {}),
    )


def publish_approved_assessment_drive(
    run_root,
    review,
    approval,
    development_gate,
    adapter,
    destination_id,
    archive_id,
    lock_path,
):
    files, hashes = approved_release_files(run_root, review, approval, development_gate)
    return publish_verified_drive_files(
        files,
        destination_id,
        archive_id,
        adapter,
        expected_hashes=hashes,
        replace_hashes=approval.get("replace_hashes", {}),
        lock_path=lock_path,
    )
