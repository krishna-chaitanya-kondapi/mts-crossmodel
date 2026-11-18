"""Build explicit Grade 5 regions from the source PDF's numbered anchor blocks."""
from pathlib import Path
import json
import sys

import pymupdf

sys.path.insert(0, str(Path("work/mts-crossmodel/src").resolve()))
from mts.products.mock_assessment.source_render import render_student

golden = Path("work/golden")
source = golden / "NY_Math_Grade5_2024_Released_Test_Questions.pdf"
maps = json.loads(Path("outputs/historical-source-item-maps.json").read_text(encoding="utf-8"))
run = next(record for record in maps if record["run_id"] == "math-grade5-2024")
ids = {row["source_number"] for row in run["items"]}
regions = []
with pymupdf.open(source) as original:
    for index in range(6, 30):
        page = original[index]
        blocks = page.get_text("blocks")
        anchors = sorted(
            (b[1], int(b[4].strip())) for b in blocks
            if b[0] < 70 and b[4].strip().isdigit() and int(b[4].strip()) in ids
        )
        for top, question in anchors:
            section_end = next((y - 12 for y, _ in anchors if y > top), 693)
            components = [
                pymupdf.Rect(b[:4]) for b in blocks
                if b[1] >= top - 10 and b[3] <= section_end and b[0] >= 35
            ]
            components += [
                rect for rect in page.cluster_drawings()
                if rect.y0 >= top - 10 and rect.y1 <= section_end and rect.x0 >= 35
            ]
            union = pymupdf.Rect(components[0])
            for rect in components[1:]:
                union |= rect
            # Some constructed responses have only a drawn work/answer region.
            if question >= 36:
                union.y1 = max(union.y1, 685)
            bounds = [max(0, union.x0 - 6), max(0, union.y0 - 6),
                      min(page.rect.width, union.x1 + 6), min(section_end, union.y1 + 6)]
            regions.append({"id": question, "source_page": index + 1, "bounds": bounds})

assert [r["id"] for r in regions] == sorted(ids)
manifest = {
    "source_sha256": run["source_sha256"],
    "title": "Grade 5 Mathematics - 2024 NYSED - source layout trial",
    "scale": 0.75,
    "regions": regions,
}
Path("outputs/grade5-source-regions.json").write_text(
    json.dumps(manifest, indent=2) + "\n", encoding="utf-8"
)
try:
    render_student(source, dict(manifest, maximum_pages=4), Path("work/grade5-four-page.pdf"))
except ValueError as exc:
    print(exc)
placements = render_student(source, manifest, Path("work/grade5-layout-trial.pdf"))
print(f"{len(placements)} regions placed on {placements[-1]['page']} pages")
Path("outputs/grade5-layout-trial-evidence.json").write_text(
    json.dumps({"maximum_pages": 4, "trial_pages": placements[-1]["page"],
                "placements": placements}, indent=2) + "\n", encoding="utf-8"
)
