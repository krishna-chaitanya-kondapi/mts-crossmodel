"""Validate and execute independent historical benchmark review RunSpecs."""

from datetime import date
from hashlib import sha256
import json
import os
from pathlib import Path
import re
import shutil
import tempfile
from time import perf_counter

import pymupdf

from .ela_student import render_ela_student
from .ela_teacher import render_ela_teacher
from .grade4_student import render_grade4_student
from .grade5_student import render_grade5_student
from .teacher_key import render_teacher_key

PROFILES = {
    "ny2024_math_grade4": (
        "grade4-student-manifest.json",
        "grade4-teacher-manifest.json",
        28,
        19,
        9,
        4,
        1,
    ),
    "ny2024_math_grade5": (
        "grade5-student-manifest.json",
        "grade5-teacher-manifest.json",
        28,
        19,
        9,
        4,
        1,
    ),
    "ny2025_ela_grade6": (
        "ela-student-manifest.json",
        "ela-teacher-manifest.json",
        14,
        12,
        2,
        4,
        2,
    ),
}


def validate_runspec(spec):
    required = {
        "version",
        "run_id",
        "profile",
        "instructional_monday",
        "purpose",
        "academic_length",
        "source_filename",
        "source_sha256",
        "blueprint",
        "presentation",
        "execution",
        "estimated_runtime_seconds",
        "estimate_basis",
    }
    if set(spec) != required or spec["version"] != 1:
        raise ValueError("RunSpec version or field set is invalid")
    if not isinstance(spec["run_id"], str) or not re.fullmatch(
        r"[a-z0-9][a-z0-9_-]{0,79}", spec["run_id"]
    ):
        raise ValueError("Run ID must be a safe identifier")
    profile = spec["profile"]
    if profile not in PROFILES:
        raise ValueError("Unsupported historical benchmark profile")
    instructional = date.fromisoformat(spec["instructional_monday"])
    if instructional.weekday() != 0:
        raise ValueError("Instructional date must be a Monday")
    expected_length = "mini" if profile == "ny2025_ela_grade6" else "full"
    if spec["purpose"] != "benchmark" or spec["academic_length"] != expected_length:
        raise ValueError("Purpose or academic length differs from the historical scope")
    filename = spec["source_filename"]
    if (
        not isinstance(filename, str)
        or "/" in filename
        or "\\" in filename
        or not filename.endswith(".pdf")
    ):
        raise ValueError("Source filename must be a PDF basename")
    if not re.fullmatch(r"[a-f0-9]{64}", spec["source_sha256"]):
        raise ValueError("RunSpec requires the exact source SHA256")
    _, _, total, mc, cr, maximum, key_pages = PROFILES[profile]
    if spec["blueprint"] != {
        "items": total,
        "multiple_choice": mc,
        "constructed_response": cr,
    }:
        raise ValueError("Blueprint differs from the fixed benchmark selection")
    if spec["presentation"] != {
        "paper": "US_Letter",
        "orientation": "portrait",
        "student_maximum_pages": maximum,
        "teacher_target_pages": key_pages,
    }:
        raise ValueError("Presentation differs from the historical constraints")
    if spec["execution"] != "local_review":
        raise ValueError("The development runner requires local_review execution")
    estimate = spec["estimated_runtime_seconds"]
    if (
        isinstance(estimate, bool)
        or not isinstance(estimate, (int, float))
        or not 0 < estimate < 86400
    ):
        raise ValueError("Runtime estimate must be positive and finite")
    if (
        not isinstance(spec["estimate_basis"], str)
        or not spec["estimate_basis"].strip()
    ):
        raise ValueError("Runtime estimate needs its basis")
    return spec


def render_runspec(spec, destination):
    rows = [
        f'Run {spec["run_id"]}',
        f'Profile {spec["profile"]}',
        f'Purpose {spec["purpose"]}, academic length {spec["academic_length"]}',
        f'Instructional Monday {spec["instructional_monday"]}',
        f'Source {spec["source_filename"]}',
        f'Source SHA256 {spec["source_sha256"]}',
        f'Blueprint {spec["blueprint"]["items"]} items, {spec["blueprint"]["multiple_choice"]} MC, '
        f'{spec["blueprint"]["constructed_response"]} CR',
        f'Student ceiling {spec["presentation"]["student_maximum_pages"]} pages; '
        f'teacher target {spec["presentation"]["teacher_target_pages"]} pages',
        f'Estimated runtime {spec["estimated_runtime_seconds"]:.2f} seconds',
        f'Estimate basis {spec["estimate_basis"]}',
        "Execution local review. Artifact-specific human approval is required for production publication.",
    ]
    with pymupdf.open() as pdf:
        page = pdf.new_page(width=612, height=792)
        page.insert_text(
            (36, 44), "Mock Assessment RunSpec", fontsize=16, fontname="hebo"
        )
        y = 78
        font = pymupdf.Font("helv")
        for row in rows:
            words = row.split()
            line = ""
            for word in words:
                candidate = f"{line} {word}".strip()
                if line and font.text_length(candidate, fontsize=10) > 540:
                    page.insert_text((36, y), line, fontsize=10)
                    y += 14
                    line = word
                else:
                    line = candidate
            if y > 736:
                raise ValueError("RunSpec summary exceeds one page")
            page.insert_text((36, y), line, fontsize=10)
            y += 24
        pdf.save(destination, deflate=True)


def run_benchmark(spec_path, source_root, output_root, fixtures):
    started = perf_counter()
    spec = validate_runspec(json.loads(Path(spec_path).read_text(encoding="utf-8-sig")))
    source = Path(source_root) / spec["source_filename"]
    if sha256(source.read_bytes()).hexdigest() != spec["source_sha256"]:
        raise ValueError("Official source bytes differ from the RunSpec")
    profile = spec["profile"]
    student_fixture, teacher_fixture, *_ = PROFILES[profile]
    student_manifest = json.loads(
        (Path(fixtures) / student_fixture).read_text(encoding="utf-8-sig")
    )
    teacher_manifest = json.loads(
        (Path(fixtures) / teacher_fixture).read_text(encoding="utf-8-sig")
    )
    if student_manifest["source_sha256"] != spec["source_sha256"]:
        raise ValueError("Student manifest and RunSpec source fingerprints differ")
    root = Path(output_root).resolve()
    root.mkdir(parents=True, exist_ok=True)
    phases = ["01-PreRun", "02-Run", "03-PostRun"]
    targets = [
        root / phase / spec["instructional_monday"] / spec["run_id"] for phase in phases
    ]
    lock = root / f'.{spec["run_id"]}.lock'
    descriptor = os.open(lock, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
    os.close(descriptor)
    moved = []
    try:
        if any(target.exists() for target in targets):
            raise FileExistsError(
                "A run with this identity already exists; select a new run ID"
            )
        with tempfile.TemporaryDirectory(prefix=".mock-", dir=root) as staging:
            stage = Path(staging)
            pre, run, post = [stage / phase for phase in phases]
            for folder in (pre, run, post):
                folder.mkdir()
            (pre / "runspec.json").write_bytes(
                (json.dumps(spec, indent=2) + "\n").encode()
            )
            render_runspec(spec, pre / "runspec.pdf")
            content_started = perf_counter()
            student = run / "student.pdf"
            teacher = run / "teacher.pdf"
            if profile == "ny2024_math_grade4":
                placements = render_grade4_student(source, student_manifest, student)
            elif profile == "ny2024_math_grade5":
                placements = render_grade5_student(source, student_manifest, student)
            else:
                placements = render_ela_student(source, student_manifest, student)
            if profile == "ny2025_ela_grade6":
                render_ela_teacher(teacher_manifest, teacher)
            else:
                render_teacher_key(
                    teacher_manifest["items"],
                    teacher_manifest["solutions"],
                    teacher,
                    title=teacher_manifest["title"],
                )
            rendering_seconds = perf_counter() - content_started
            with pymupdf.open(student) as pupils, pymupdf.open(teacher) as teachers:
                if len(pupils) > spec["presentation"]["student_maximum_pages"]:
                    raise ValueError("Student pagination failed")
                if len(teachers) != spec["presentation"]["teacher_target_pages"]:
                    raise ValueError("Teacher pagination failed")
                if not all(
                    tuple(p.rect) == (0, 0, 612, 792)
                    for pdf in (pupils, teachers)
                    for p in pdf
                ):
                    raise ValueError("Paper size check failed")
                if len(placements) != spec["blueprint"]["items"]:
                    raise ValueError("Question placement count failed")
                result = {
                    "status": "REVIEW_REQUIRED",
                    "run_id": spec["run_id"],
                    "profile": profile,
                    "student_pages": len(pupils),
                    "teacher_pages": len(teachers),
                    "structural_checks": "PASS",
                    "academic_review": "NOT_VERIFIED",
                    "source_fidelity": "NOT_VERIFIED",
                    "visual_review": "NOT_VERIFIED",
                    "production_publications": 0,
                    "estimated_runtime_seconds": spec["estimated_runtime_seconds"],
                    "rendering_seconds": rendering_seconds,
                    "actual_active_seconds": perf_counter() - started,
                    "placements": placements,
                    "artifacts": {
                        p.name: sha256(p.read_bytes()).hexdigest()
                        for p in (
                            student,
                            teacher,
                            pre / "runspec.pdf",
                            pre / "runspec.json",
                        )
                    },
                    "input_hashes": {
                        "source": spec["source_sha256"],
                        "student_manifest": sha256(
                            (Path(fixtures) / student_fixture).read_bytes()
                        ).hexdigest(),
                        "teacher_manifest": sha256(
                            (Path(fixtures) / teacher_fixture).read_bytes()
                        ).hexdigest(),
                    },
                }
            (post / "runlog.json").write_bytes(
                (json.dumps(result, indent=2) + "\n").encode()
            )
            (post / "review.md").write_bytes(
                b"# Mock Assessment review\n\nStructural checks passed. Academic, source and visual reviews remain open.\n"
            )
            for folder, target in zip((pre, run, post), targets):
                target.parent.mkdir(parents=True, exist_ok=True)
                os.rename(folder, target)
                moved.append(target)
        return result
    except Exception:
        for target in moved:
            shutil.rmtree(target)
        raise
    finally:
        lock.unlink()
