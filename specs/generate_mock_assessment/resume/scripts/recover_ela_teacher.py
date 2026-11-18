"""Recover the historical YPQA content into an inspectable canonical teacher manifest."""
from pathlib import Path
import hashlib
import json
import re
import pymupdf

path=Path("work/golden/MTS-ELA-RC-6thGrade-WeeklyWorksheet-2026-09-28-KEY.pdf")
pages=[]
with pymupdf.open(path) as original:
    for page in original:
        blocks=[b[4] for b in page.get_text("blocks",sort=True)
                if b[1]<720]
        pages.append("\n".join(blocks))
text="\n".join(pages)
expected=list("BCDBAADB DDBA".replace(" ",""))
answers=re.findall(r"Correct Answer:\s*([A-D])",text)
assert answers==expected
manifest={
 "title":"Grade 6 ELA | NYSED 2025 | Teacher review copy",
 "historical_key_sha256":hashlib.sha256(path.read_bytes()).hexdigest(),
 "provenance":"Historical delivered YPQA key. Model responses remain MTS-authored.",
 "pages":pages, "official_answers":answers,
 "source_numbers":[*range(8,15),*range(22,29)],
}
Path("work/ela-teacher-manifest.json").write_text(json.dumps(manifest,indent=2)+"\n",encoding="utf-8")
