"""Carry forward completed reviews only for identical verified benchmark inputs and pages."""

from hashlib import sha256
import json
from pathlib import Path

import pymupdf

QUALITY_FIELDS = ("academic_review", "source_fidelity", "visual_review")


def manifest_fingerprint(value):
    encoded = json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=True
    ).encode()
    return sha256(encoded).hexdigest()


def implementation_fingerprints(folder):
    return {
        path.name: sha256(
            path.read_bytes().replace(b"\r\n", b"\n").removeprefix(b"\xef\xbb\xbf")
        ).hexdigest()
        for path in sorted(Path(folder).glob("*.py"))
    }


def page_fingerprints(path):
    with pymupdf.open(path) as pdf:
        return [
            sha256(page.get_pixmap(alpha=False).samples).hexdigest() for page in pdf
        ]


def match_frozen_review(
    profile,
    fixtures,
    *,
    source_sha256,
    student_manifest_sha256,
    teacher_manifest_sha256,
    implementation_hashes,
    student,
    teacher
):
    pending = {field: "NOT_VERIFIED" for field in QUALITY_FIELDS}
    catalog_path = Path(fixtures).parent / "verified-profiles.json"
    if not catalog_path.is_file():
        return pending | {"review_match": "No verified-profile catalog"}
    catalog = json.loads(catalog_path.read_text(encoding="utf-8-sig"))
    record = catalog.get("profiles", {}).get(profile)
    if not record:
        return pending | {"review_match": "Profile has no frozen review"}
    actual = {
        "source_sha256": source_sha256,
        "student_manifest_sha256": student_manifest_sha256,
        "teacher_manifest_sha256": teacher_manifest_sha256,
        "implementation_hashes": implementation_hashes,
        "renderer_version": pymupdf.VersionBind,
        "student_page_pixels": page_fingerprints(student),
        "teacher_page_pixels": page_fingerprints(teacher),
    }
    if any(record.get(key) != value for key, value in actual.items()):
        return pending | {
            "review_match": "Inputs, implementation, renderer version or page pixels changed"
        }
    root = Path(fixtures).resolve().parents[2]
    evidence = record.get("evidence", [])
    if not evidence:
        return pending | {"review_match": "Completed-review evidence is missing"}
    for entry in evidence:
        path = (root / entry["path"]).resolve()
        if (
            not path.is_relative_to(root)
            or not path.is_file()
            or sha256(path.read_bytes()).hexdigest() != entry["sha256"]
        ):
            return pending | {
                "review_match": "Completed-review evidence changed or is unavailable"
            }
    if any(record.get(field) != "PASS" for field in QUALITY_FIELDS):
        return pending | {"review_match": "Profile review is incomplete"}
    return {field: "PASS" for field in QUALITY_FIELDS} | {
        "review_match": "Exact reviewed inputs, implementation and rendered pages",
        "review_evidence": evidence,
    }
