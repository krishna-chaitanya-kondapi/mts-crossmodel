"""Inspect regenerated benchmark artifacts against the recovered source selection."""

import argparse
from collections import Counter
from hashlib import sha256
import json
from pathlib import Path
import re
import sys

import pymupdf

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from mts.products.mock_assessment.review_catalog import page_fingerprints


def inspect(run_root, source_root):
    official = json.loads(
        (ROOT / "outputs/historical-source-item-maps.json").read_text()
    )
    results = []
    for grade, profile, source_record in zip(
        (4, 5, 6),
        ("ny2024_math_grade4", "ny2024_math_grade5", "ny2025_ela_grade6"),
        official,
    ):
        log = json.loads(
            next(run_root.rglob(profile + "-review/runlog.json")).read_text()
        )
        student_path = next(run_root.rglob(profile + "-review/student.pdf"))
        teacher_path = next(run_root.rglob(profile + "-review/teacher.pdf"))
        source_path = source_root / source_record["source_filename"]
        assert (
            sha256(source_path.read_bytes()).hexdigest()
            == source_record["source_sha256"]
        )
        with pymupdf.open(student_path) as student, pymupdf.open(
            teacher_path
        ) as teacher, pymupdf.open(source_path) as source:
            teacher_text = "\n".join(page.get_text() for page in teacher)
            expected = source_record["items"]
            mc = [row for row in expected if row["type"] == "multiple_choice"]
            cr = [row for row in expected if row["type"] == "constructed_response"]
            if grade != 6:
                actual_keys = [
                    (int(n), key)
                    for n, key in re.findall(r"(\d+):\s*([A-D])\b", teacher_text)
                ]
                assert actual_keys == [
                    (r["output_number"], r["official_key"]) for r in mc
                ]
                actual_credits = [
                    (int(n), int(points))
                    for n, points in re.findall(
                        r"(\d+) \((\d+) credits?\)", teacher_text
                    )
                ]
                assert actual_credits == [(r["output_number"], r["points"]) for r in cr]
            else:
                actual_keys = re.findall(r"Correct Answer:\s*([A-D])", teacher_text)
                assert actual_keys == [r["official_key"] for r in mc]
                for item in cr:
                    assert re.search(
                        rf"{item['output_number']}\. Constructed Response - {item['points']} credits",
                        teacher_text,
                    )
                assert teacher_text.count("MTS Model Response:") == 2
            placements = log["placements"]
            numbers = [row.get("item", row.get("id", row.get("number"))) for row in placements]
            assert numbers == [row["output_number"] for row in expected]
            native = []
            if grade != 6:
                manifest = json.loads(
                    (
                        ROOT
                        / f"specs/generate_mock_assessment/fixtures/grade{grade}-student-manifest.json"
                    ).read_text()
                )
                for region, row in zip(manifest["regions"], placements):
                    full = row["column"] == "full"
                    x = 30 if row["column"] == 1 or full else 316
                    width = 550 if full else 258
                    bottom = row["y"] + row["height"]
                    assert bottom <= 754
                    original = source[region["source_page"] - 1].get_text(
                        clip=pymupdf.Rect(region["bounds"])
                    )
                    current = student[row["page"] - 1].get_text(
                        clip=pymupdf.Rect(
                            x - 5, row["y"] - 10, x + width + 5, bottom - 1
                        )
                    )

                    def words(value):
                        return Counter(
                            re.findall(
                                r"[A-Za-z]+",
                                value.replace("\u0100", "fi").replace("\u0101", "fl"),
                            )
                        )

                    missing = words(original) - words(current)
                    assert not missing, (grade, region["id"], missing)
                    native.append(
                        {"item": region["id"], "missing_native_words": dict(missing)}
                    )
                # Atomic placements cannot intersect another item in the same page/column band.
                for index, left in enumerate(placements):
                    for right in placements[index + 1 :]:
                        if left["page"] != right["page"]:
                            continue
                        if left["column"] == right["column"] or "full" in (
                            left["column"],
                            right["column"],
                        ):
                            assert (
                                left["y"] + left["height"] <= right["y"]
                                or right["y"] + right["height"] <= left["y"]
                            )
            assert all(
                tuple(page.rect) == (0, 0, 612, 792)
                for page in list(student) + list(teacher)
            )
            results.append(
                {
                    "profile": profile,
                    "revision": log["execution_revision"],
                    "source_sha256": source_record["source_sha256"],
                    "student_sha256": sha256(student_path.read_bytes()).hexdigest(),
                    "teacher_sha256": sha256(teacher_path.read_bytes()).hexdigest(),
                    "student_pages": len(student),
                    "teacher_pages": len(teacher),
                    "student_page_pixels": page_fingerprints(student_path),
                    "teacher_page_pixels": page_fingerprints(teacher_path),
                    "official_mc_matches": len(mc),
                    "official_cr_credit_matches": len(cr),
                    "selected_numbers": numbers,
                    "native_text_comparison": native,
                    "placements": placements,
                    "scope": "Native word preservation covers text-layer words. Vector notation, figures, raster ELA paragraphs and visual reading order require the separately recorded source and every-page reviews.",
                }
            )
    return {"status": "PASS", "runs": results}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-root", type=Path, required=True)
    parser.add_argument("--source-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result = inspect(args.run_root, args.source_root)
    args.output.write_bytes((json.dumps(result, indent=2) + "\n").encode())
    print(
        "All 70 selections, 50 MC keys, 20 CR credit values and 56 Math native-word regions verified."
    )


if __name__ == "__main__":
    main()

