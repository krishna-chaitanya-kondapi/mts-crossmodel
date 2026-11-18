from pathlib import Path
import hashlib
import json
import sys

import pymupdf

sys.path.insert(0, str(Path("work/mts-crossmodel/src").resolve()))
from mts.products.mock_assessment.item_map import select_items

runs = [
    ("math-grade4-2024", "NY_Math_Grade4_2024", [1,2,7,10,11,12,15,16,22,23,24,26,29,30,31,32,33,34,35,*range(36,45)], False),
    ("math-grade5-2024", "NY_Math_Grade5_2024", [1,2,3,4,7,9,10,12,15,16,19,27,28,*range(30,45)], False),
    ("ela-grade6-2025", "NY_ELA_Grade6_2025", [*range(8,15),*range(22,29)], True),
]
inventory = []
for run_id, stem, selection, renumber in runs:
    path = Path("work/golden") / f"{stem}_Released_Test_Questions.pdf"
    with pymupdf.open(path) as source:
        text = source[-1].get_text(sort=True)
        page_number = len(source)
    items = select_items(text, selection, renumber=renumber)
    inventory.append(dict(run_id=run_id, source_filename=path.name,
                          source_sha256=hashlib.sha256(path.read_bytes()).hexdigest(),
                          item_map_pdf_page=page_number, items=items))
    print(run_id, len(items), sum(i["official_key"] is not None for i in items),
          sum(i["official_key"] is None for i in items), page_number)
    if run_id.startswith("math-grade4"):
        print("Official released IDs:", [int(line.split()[0]) for line in text.splitlines()
              if "Multiple Choice" in line or "Constructed Response" in line
              if line.split()[0].isdigit()])
Path("outputs/historical-source-item-maps.json").write_text(
    json.dumps(inventory, indent=2) + "\n", encoding="utf-8"
)
