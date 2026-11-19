"""Validate the supported source-based Mock Assessment draft RunSpec."""
from pathlib import Path

from .verification import digest


def _section(parent: dict[str, object], name: str) -> dict[str, object]:
    value = parent.get(name)
    if not isinstance(value, dict):
        raise ValueError(f"{name} must be an object")
    return value


def _integer(values: dict[str, object], name: str, minimum: int) -> int:
    value = values.get(name)
    if not isinstance(value, int) or isinstance(value, bool) or value < minimum:
        raise ValueError(f"{name} must be an integer >= {minimum}")
    return value


def validate_draft(spec: object, source_path: Path) -> None:
    """Check structure and source identity, not authorization or approval."""
    if not isinstance(spec, dict):
        raise ValueError("RunSpec must be an object")
    run = _section(spec, "run")
    if run.get("worksheet_type") != "mock_assessment" or run.get("subject") not in ("math", "ela"):
        raise ValueError("Expected a Math or ELA Mock Assessment")
    _integer(run, "grade", 1)

    assessment = _section(spec, "assessment")
    if assessment.get("purpose") != "benchmark":
        raise ValueError("Draft preflight currently supports benchmark purpose only")
    if assessment.get("length") not in ("full", "mini", "custom"):
        raise ValueError("Assessment length must be full, mini, or custom")

    source = _section(spec, "source")
    if source.get("mode") != "source_based":
        raise ValueError("Draft preflight currently supports source_based mode only")
    rights = source.get("rights_basis")
    if not isinstance(rights, str) or not rights.strip():
        raise ValueError("Source rights_basis must identify a documented basis")
    if not source_path.is_file():
        raise ValueError("Source file does not exist")
    if source.get("sha256") != digest(source_path):
        raise ValueError("Source SHA-256 does not match the RunSpec")

    blueprint = _section(spec, "blueprint")
    total = _integer(blueprint, "questions", 1)
    if _integer(blueprint, "multiple_choice", 0) + _integer(blueprint, "constructed_response", 0) != total:
        raise ValueError("Question format counts must sum to blueprint.questions")

    presentation = _section(spec, "presentation")
    if presentation.get("paper_size") != "US_Letter" or presentation.get("orientation") != "portrait":
        raise ValueError("Draft preflight supports portrait US_Letter only")
    pagination = _section(presentation, "student_pagination")
    if pagination.get("policy") not in ("maximum", "exact", "target"):
        raise ValueError("Invalid student pagination policy")
    _integer(pagination, "pages", 1)
