"""Render all historical benchmark review pairs and record structural evidence."""

import argparse
from hashlib import sha256
import json
from pathlib import Path
import re
import subprocess
import sys

import pymupdf

ROOT = Path(__file__).resolve().parents[1]
FIXTURES = ROOT / "specs/generate_mock_assessment/fixtures"
CLI = ROOT / "scripts/generate_mock_assessment.py"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    records = []
    for (
        label,
        mode,
        source_name,
        student_manifest,
        teacher_manifest,
        ceiling,
        key_pages,
    ) in [
        (
            "grade4",
            "grade4-student",
            "NY_Math_Grade4_2024_Released_Test_Questions.pdf",
            "grade4-student-manifest.json",
            "grade4-teacher-manifest.json",
            4,
            1,
        ),
        (
            "grade5",
            "grade5-student",
            "NY_Math_Grade5_2024_Released_Test_Questions.pdf",
            "grade5-student-manifest.json",
            "grade5-teacher-manifest.json",
            4,
            1,
        ),
        (
            "ela6",
            "ela-student",
            "NY_ELA_Grade6_2025_Released_Test_Questions.pdf",
            "ela-student-manifest.json",
            "ela-teacher-manifest.json",
            4,
            2,
        ),
    ]:
        student = args.output / f"{label}-student.pdf"
        teacher = args.output / f"{label}-teacher.pdf"
        placements = args.output / f"{label}-placements.json"
        source = args.source_root / source_name
        manifest = json.loads(
            (FIXTURES / student_manifest).read_text(encoding="utf-8-sig")
        )
        if sha256(source.read_bytes()).hexdigest() != manifest["source_sha256"]:
            raise ValueError(f"Source mismatch for {label}")
        commands = [
            [
                sys.executable,
                str(CLI),
                mode,
                "--source",
                str(source),
                "--manifest",
                str(FIXTURES / student_manifest),
                "--output",
                str(student),
                "--placements",
                str(placements),
            ],
            [
                sys.executable,
                str(CLI),
                "ela-teacher" if label == "ela6" else "teacher-key",
                "--manifest",
                str(FIXTURES / teacher_manifest),
                "--output",
                str(teacher),
            ],
        ]
        for command in commands:
            subprocess.run(command, cwd=ROOT, check=True)
        with pymupdf.open(student) as pupils, pymupdf.open(teacher) as teachers:
            if not len(pupils) <= ceiling or len(teachers) != key_pages:
                raise ValueError(f"Pagination failed for {label}")
            if not all(
                tuple(page.rect) == (0, 0, 612, 792)
                for pdf in [pupils, teachers]
                for page in pdf
            ):
                raise ValueError(f"Paper size failed for {label}")
            if label == "ela6" and len(pupils) != 4:
                raise ValueError("ELA historical student profile must have four pages")
            rows = json.loads(placements.read_text())["placements"]
            expected = (
                [q["output_number"] for q in manifest["questions"]]
                if label == "ela6"
                else [q["id"] for q in manifest["regions"]]
            )
            observed = [
                r["number"] if label == "ela6" else r.get("id", r.get("item"))
                for r in rows
            ]
            if observed != expected:
                raise ValueError(f"Item order failed for {label}")
            record = {
                "run": label,
                "student_pages": len(pupils),
                "student_ceiling": ceiling,
                "teacher_pages": len(teachers),
                "teacher_target": key_pages,
                "items": expected,
                "letter_portrait": True,
                "commands": [c[2:] for c in commands],
                "artifacts": {
                    p.name: sha256(p.read_bytes()).hexdigest()
                    for p in [student, teacher, placements]
                },
            }
            records.append(record)
    report = {
        "revision": subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True
        ).strip(),
        "status": "STRUCTURAL_PASS",
        "scope": "Executed three student/teacher pairs; pagination, paper, order and artifact fingerprints.",
        "limitations": "Academic, full source and visual/golden equivalence require separate evidence.",
        "runs": records,
    }
    (args.output / "regression-structure.json").write_bytes(
        (json.dumps(report, indent=2) + "\n").encode()
    )
    print("Three benchmark pairs rendered and structurally checked.")


if __name__ == "__main__":
    main()
