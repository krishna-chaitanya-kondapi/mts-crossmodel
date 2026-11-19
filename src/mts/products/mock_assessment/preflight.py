"""Validate the supported source-based Mock Assessment draft RunSpec."""
from hashlib import sha256
import json
from pathlib import Path
import textwrap

import pymupdf


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


def validate_draft(spec: object, source_path: Path) -> dict[str, object]:
    """Check structure and source identity, not authorization or approval."""
    if not isinstance(spec, dict):
        raise ValueError("RunSpec must be an object")
    if {"status", "approval", "approved", "release"} & spec.keys():
        raise ValueError("Draft input cannot contain status, approval, or release fields")
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
    source_bytes = source_path.read_bytes()
    if source.get("sha256") != sha256(source_bytes).hexdigest():
        raise ValueError("Source SHA-256 does not match the RunSpec")

    blueprint = _section(spec, "blueprint")
    total = _integer(blueprint, "questions", 1)
    counts = {kind: _integer(blueprint, kind, 0) for kind in ("multiple_choice", "constructed_response")}
    if sum(counts.values()) != total:
        raise ValueError("Question format counts must sum to blueprint.questions")

    selection = source.get("selection")
    if not isinstance(selection, list) or len(selection) != total:
        raise ValueError("Source selection must contain one entry per blueprint question")
    try:
        with pymupdf.open(stream=source_bytes, filetype="pdf") as document:
            if not document.is_pdf or document.needs_pass or not document.page_count:
                raise ValueError("Source must be a readable, unencrypted PDF")
            page_count = document.page_count
    except pymupdf.FileDataError as error:
        raise ValueError("Source must be a readable PDF") from error
    observed = dict.fromkeys(counts, 0)
    selected_ids: set[int] = set()
    for item in selection:
        if not isinstance(item, dict):
            raise ValueError("Each source selection entry must be an object")
        number = _integer(item, "source_number", 1)
        if number in selected_ids:
            raise ValueError("Source selection question numbers must be unique")
        selected_ids.add(number)
        if _integer(item, "source_page", 1) > page_count:
            raise ValueError("Source selection page exceeds the PDF page count")
        kind = item.get("type")
        if not isinstance(kind, str) or kind not in counts:
            raise ValueError("Invalid source selection question type")
        observed[kind] += 1
    if observed != counts:
        raise ValueError("Source selection format counts must match the blueprint")

    presentation = _section(spec, "presentation")
    if presentation.get("paper_size") != "US_Letter" or presentation.get("orientation") != "portrait":
        raise ValueError("Draft preflight supports portrait US_Letter only")
    pagination = _section(presentation, "student_pagination")
    if pagination.get("policy") not in ("maximum", "exact", "target"):
        raise ValueError("Invalid student pagination policy")
    _integer(pagination, "pages", 1)
    return spec


def write_review_bundle(draft: dict[str, object], output_dir: Path) -> None:
    """Write the validated draft, never an approval or a release record."""
    record = {
        "status": "DRAFT",
        "rights_verified": False,
        "human_approval_verified": False,
        "runspec": draft,
    }
    text = json.dumps(record, indent=2, sort_keys=True, allow_nan=False)
    with pymupdf.open() as pdf:
        lines = [
            line
            for record_line in text.splitlines()
            for line in textwrap.wrap(record_line, width=88, drop_whitespace=False)
        ]
        for offset in range(0, len(lines), 48):
            page = pdf.new_page(width=612, height=792)
            page.insert_text((36, 36), "Mock Assessment RunSpec - Draft, not approved", fontsize=13)
            for index, line in enumerate(lines[offset:offset + 48]):
                page.insert_text((36, 60 + index * 14), line, fontname="cour", fontsize=9)
        pdf_bytes = pdf.tobytes()
    output_dir.mkdir()
    (output_dir / "runspec.json").write_bytes((text + "\n").encode("utf-8"))
    (output_dir / "runspec.pdf").write_bytes(pdf_bytes)
