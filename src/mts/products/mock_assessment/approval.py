"""Bind a trusted operator's pre-run decision to the exact review packet."""
from collections.abc import Callable, Mapping
from hashlib import sha256
import hmac
import json
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import TypeVar

from .preflight import validate_draft
from .source_render import render_student

Result = TypeVar("Result")
_DECISION_FIELDS = frozenset({
    "decision", "scope", "reviewer", "runspec_json_sha256", "runspec_pdf_sha256",
})


def _verify_decision(decision: Mapping[str, object], key: bytes) -> dict[str, object]:
    if not isinstance(key, bytes) or len(key) < 32:
        raise ValueError("A trusted approval key of at least 32 bytes is required")
    record = dict(decision)
    mac = record.pop("hmac_sha256", None)
    if record.keys() != _DECISION_FIELDS or not all(isinstance(value, str) for value in record.values()):
        raise ValueError("Invalid signed pre-run decision fields")
    payload = json.dumps(record, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("ascii")
    expected = hmac.digest(key, b"mts/mock-assessment/pre-run/v1\0" + payload, "sha256").hex()
    if not isinstance(mac, str) or not mac.isascii() or not hmac.compare_digest(mac, expected):
        raise ValueError("Pre-run decision authentication failed")
    return record


def run_approved_draft(
    review_dir: Path,
    source_path: Path,
    decision: Mapping[str, object],
    execute: Callable[[dict[str, object]], Result],
    *,
    approval_key: bytes,
) -> Result:
    """Dispatch a draft only after verifying a decision from a trusted issuer."""
    decision = _verify_decision(decision, approval_key)
    reviewer = decision.get("reviewer")
    if (
        decision.get("decision") != "APPROVED"
        or decision.get("scope") != "PRE_RUN"
        or not isinstance(reviewer, str)
        or not reviewer.strip()
    ):
        raise ValueError("A separate pre-run approval is required")
    packet_json = (review_dir / "runspec.json").read_bytes()
    packet_pdf = (review_dir / "runspec.pdf").read_bytes()
    if (
        decision.get("runspec_json_sha256") != sha256(packet_json).hexdigest()
        or decision.get("runspec_pdf_sha256") != sha256(packet_pdf).hexdigest()
    ):
        raise ValueError("Approval does not match the current RunSpec review packet")

    packet = json.loads(packet_json)
    if not isinstance(packet, dict) or packet.get("status") != "DRAFT":
        raise ValueError("Approval must refer to a RunSpec draft packet")
    draft = validate_draft(packet.get("runspec"), source_path)
    return execute(draft)


def render_approved_student(
    review_dir: Path,
    source_path: Path,
    decision: Mapping[str, object],
    destination: Path,
    *,
    approval_key: bytes,
) -> None:
    """Render an image-only local draft; the issuer must separately verify source rights."""
    def execute(draft: dict[str, object]) -> None:
        source = draft["source"]
        presentation = draft["presentation"]
        assert isinstance(source, dict) and isinstance(presentation, dict)
        selection = source["selection"]
        pagination = presentation["student_pagination"]
        regions = []
        for item in selection:
            bounds = item.get("bounds")
            if (
                not isinstance(bounds, list)
                or len(bounds) != 4
                or not all(type(value) in (int, float) for value in bounds)
            ):
                raise ValueError(f"Approved source item {item['source_number']} requires four numeric bounds")
            regions.append({"id": item["source_number"], "source_page": item["source_page"], "bounds": bounds})

        with TemporaryDirectory(prefix="mock-approved-") as directory:
            candidate = Path(directory) / "student.pdf"
            manifest = {
                "title": "Mock Assessment - Local review",
                "source_sha256": source["sha256"],
                "scale": 0.75,
                "regions": regions,
            }
            if pagination["policy"] in ("maximum", "exact"):
                manifest["maximum_pages"] = pagination["pages"]
            placements = render_student(source_path, manifest, candidate, rasterize_crops=True)
            if pagination["policy"] == "exact" and placements[-1]["page"] != pagination["pages"]:
                raise ValueError("Student PDF does not meet the approved exact page count")
            with destination.open("xb") as output:
                output.write(candidate.read_bytes())

    run_approved_draft(review_dir, source_path, decision, execute, approval_key=approval_key)
