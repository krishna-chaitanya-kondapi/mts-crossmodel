"""Compare the paired Grade 5 CLI outputs to the delivered historical PDFs."""
from hashlib import sha256
import json
from pathlib import Path

import pymupdf

root = Path("work")
golden = root / "golden"
placements = json.loads((root / "grade5-student-cli-placements.json").read_text())["placements"]
expected = [1, 2, 3, 4, 7, 9, 10, 12, 15, 16, 19, 27, 28, *range(30, 45)]
assert [row["id"] for row in placements] == expected


def inspect(path):
    with pymupdf.open(path) as doc:
        return {
            "filename": path.name, "sha256": sha256(path.read_bytes()).hexdigest(),
            "pages": len(doc),
            "letter_portrait": all(tuple(page.rect) == (0, 0, 612, 792) for page in doc),
        }


student = inspect(root / "grade5-student-cli.pdf")
teacher = inspect(root / "grade5-teacher-cli.pdf")
historical_student = inspect(golden / "MTS-NY-Math-Grade5-2024-Worksheet.pdf")
historical_teacher = inspect(golden / "MTS-NY-Math-Grade5-2024-Answer-Key.pdf")
assert all(r["letter_portrait"] for r in (student, teacher, historical_student, historical_teacher))
assert student["pages"] <= 4 and teacher["pages"] == 1
data = {
    "status": "NOT_DONE",
    "reference": "Grade 5 final delivered worksheet and teacher key",
    "student": {"golden": historical_student, "regenerated": student},
    "teacher": {"golden": historical_teacher, "regenerated": teacher},
    "student_item_order": expected,
    "differences": [
        "Student and teacher page counts match. Item placements differ, and inline fractions use slash notation.",
        "Teacher key uses horizontal answer rows and explicit constructed-response credit labels.",
        "Full comparison of source content, official rubrics, diagram bounds, and print readability remains open.",
    ],
}
Path("outputs/grade5-golden-comparison.json").write_text(json.dumps(data, indent=2) + "\n")
print(f"Student: delivered {historical_student['pages']} pages, regenerated {student['pages']}; "
      f"teacher: delivered {historical_teacher['pages']}, regenerated {teacher['pages']}.")

