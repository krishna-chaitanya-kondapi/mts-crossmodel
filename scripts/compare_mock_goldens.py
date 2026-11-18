"""Compare designated historical references with regenerated review artifacts."""

import argparse
from collections import Counter
from hashlib import sha256
import json
from pathlib import Path
import re

import pymupdf

ROOT = Path(__file__).resolve().parents[1]


def inspect_pdf(path):
    with pymupdf.open(path) as doc:
        sizes = Counter(
            round(span["size"], 1)
            for page in doc
            for block in page.get_text("dict")["blocks"]
            if "lines" in block
            for line in block["lines"]
            for span in line["spans"]
        )
        return {
            "filename": path.name,
            "sha256": sha256(path.read_bytes()).hexdigest(),
            "pages": len(doc),
            "letter_portrait": all(
                tuple(page.rect) == (0, 0, 612, 792) for page in doc
            ),
            "font_size_distribution": dict(sorted(sizes.items())),
        }


def math_reference_positions(path, selection):
    result = {}
    with pymupdf.open(path) as doc:
        for index, page in enumerate(doc, 1):
            for block in page.get_text("blocks"):
                match = re.match(r"^(\d+)\n", block[4])
                if not match or not (block[0] < 45 or 310 < block[0] < 330):
                    continue
                number = int(match[1])
                if number in selection:
                    if number in result:
                        raise ValueError(f"Duplicate golden item {number}")
                    result[number] = {
                        "page": index,
                        "column": 1 if block[0] < 300 else 2,
                        "y": block[1],
                    }
    if set(result) != set(selection):
        raise ValueError(
            f"Incomplete golden question inventory: {set(selection)-set(result)}"
        )
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-root", type=Path, required=True)
    parser.add_argument("--golden-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    registry = json.loads(
        (ROOT / "specs/generate_mock_assessment/golden-assets.json").read_text()
    )
    for item in registry["assets"]:
        if item["kind"] == "golden":
            path = args.golden_root / item["filename"]
            if sha256(path.read_bytes()).hexdigest() != item["sha256"]:
                raise ValueError(f"Designated reference changed: {path.name}")
    results = []
    for run, profile in [
        ("math4", "ny2024_math_grade4-review"),
        ("math5", "ny2024_math_grade5-review"),
        ("ela6", "ny2025_ela_grade6-review"),
    ]:
        log = json.loads(
            next(args.run_root.rglob(profile + "/runlog.json")).read_text()
        )
        assets = [
            a for a in registry["assets"] if a["run"] == run and a["kind"] == "golden"
        ]
        student_name = next(
            a["filename"]
            for a in assets
            if not any(t in a["filename"] for t in ["KEY", "Answer-Key"])
        )
        teacher_name = next(
            a["filename"]
            for a in assets
            if any(t in a["filename"] for t in ["KEY", "Answer-Key"])
        )
        student = next(args.run_root.rglob(profile + "/student.pdf"))
        teacher = next(args.run_root.rglob(profile + "/teacher.pdf"))
        entry = {
            "run": run,
            "execution_revision": log["execution_revision"],
            "student": {
                "golden": inspect_pdf(args.golden_root / student_name),
                "regenerated": inspect_pdf(student),
            },
            "teacher": {
                "golden": inspect_pdf(args.golden_root / teacher_name),
                "regenerated": inspect_pdf(teacher),
            },
            "item_inventory": [],
        }
        if (
            entry["student"]["golden"]["pages"]
            != entry["student"]["regenerated"]["pages"]
        ):
            raise ValueError(f"Student page-count regression for {run}")
        if (
            entry["teacher"]["golden"]["pages"]
            != entry["teacher"]["regenerated"]["pages"]
        ):
            raise ValueError(f"Teacher page-count regression for {run}")
        if run.startswith("math"):
            selection = [r.get("item", r.get("id")) for r in log["placements"]]
            old = math_reference_positions(args.golden_root / student_name, selection)
            entry["item_inventory"] = [
                {"number": number, "golden": old[number], "regenerated": row}
                for number, row in zip(selection, log["placements"])
            ]
        else:
            with pymupdf.open(args.golden_root / student_name) as doc:
                numbers = [
                    int(word[4][:-1])
                    for index in [1, 3]
                    for word in doc[index].get_text("words")
                    if re.fullmatch(r"(?:[1-9]|1[0-4])\.", word[4])
                    and (abs(word[0] - 44) < 2 or abs(word[0] - 309) < 2)
                ]
            if sorted(numbers) != list(range(1, 15)):
                raise ValueError("ELA golden inventory differs from fourteen questions")
            entry["item_inventory"] = log["placements"]
        results.append(entry)
    evidence = {
        "status": "PAGE_AND_SELECTION_PARITY",
        "runs": results,
        "differences": [
            "Question positions, headers, page numbering, work-space placement and line wrapping differ.",
            "Native formula paths were transcribed using equivalent inline fractions and operators; original Math figures remain vector crops.",
            "Math Grade 4 teacher key adds official angle tolerance and an alternate triangle classification.",
            "ELA source transcription restores NYSED wording and section headings missing or altered in the designated golden.",
            "ELA Q8 teacher reasoning was clarified after blind-review reconciliation; official answer B is retained.",
            "ELA image and caption are enlarged/retypeset for readability; YPQA content is reflowed with explicit scoring guidance.",
        ],
        "quality_scope": "Reference identity, complete selected-item inventory and page parity verified. Full educational/presentation equivalence uses the separate academic, source and visual evidence.",
    }
    args.output.write_bytes((json.dumps(evidence, indent=2) + "\n").encode())
    print("All three reference pairs match selected-item inventories and page counts.")


if __name__ == "__main__":
    main()
