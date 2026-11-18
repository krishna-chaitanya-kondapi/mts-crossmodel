from pathlib import Path
import hashlib
import sys
import tempfile
import pymupdf
sys.path.insert(0, str(Path("work/mts-crossmodel/src").resolve()))
from mts.products.mock_assessment.source_render import render_student

with tempfile.TemporaryDirectory() as root:
    source = Path(root) / "test.pdf"
    output = Path(root) / "output.pdf"
    with pymupdf.open() as pdf:
        p = pdf.new_page(width=612, height=792)
        p.insert_text((50, 50), "Synthetic layout test")
        pdf.save(source)
    def region(id, width, height):
        return {"id": id, "source_page": 1, "bounds": [0, 0, width, height]}
    manifest = {"source_sha256": hashlib.sha256(source.read_bytes()).hexdigest(),
                "scale": 1, "title": "Layout test", "maximum_pages": 1,
                "regions": [region(1, 400, 100),region(2, 250, 500),region(3, 250, 450)]}
    rows = render_student(source, manifest, output)
    assert [r["page"] for r in rows] == [1, 1, 1]
    assert rows[2]["bounds"][0] > rows[1]["bounds"][2]
    assert rows[2]["bounds"][1] > rows[0]["bounds"][3]
    print("PASS: right column begins below full-width content; all regions fit on one page.")
