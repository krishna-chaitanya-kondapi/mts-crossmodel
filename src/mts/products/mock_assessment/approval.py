"""Bind a trusted operator's pre-run decision to the exact review packet."""
from collections.abc import Callable, Mapping
from hashlib import sha256
import json
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import TypeVar

from .preflight import validate_draft
from .source_render import render_student

Result = TypeVar("Result")


def run_approved_draft(
    review_dir: Path,
    source_path: Path,
    decision: Mapping[str, object],
    execute: Callable[[dict[str, object]], Result],
) -> Result:
    """Dispatch an approved draft. The caller must authenticate the decision."""
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
) -> None:
    """Render an image-only local crop draft after the caller verifies approval and rights."""
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

    run_approved_draft(review_dir, source_path, decision, execute)
