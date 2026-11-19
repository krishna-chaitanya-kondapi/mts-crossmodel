"""Bind a trusted operator's pre-run decision to the exact review packet."""
from collections.abc import Callable, Mapping
from hashlib import sha256
import json
from pathlib import Path
from typing import TypeVar

from .preflight import validate_draft

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
