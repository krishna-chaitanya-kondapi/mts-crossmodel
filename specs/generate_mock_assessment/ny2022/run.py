"""Regenerate the six 2022 review pairs from fingerprinted source PDFs."""
import argparse
from hashlib import sha256
import json
import os
from pathlib import Path
import subprocess
import sys
from tempfile import TemporaryDirectory

import fitz

HERE = Path(__file__).resolve().parent

def digest(path):
    return sha256(path.read_bytes()).hexdigest()

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--sources", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--font-dir", type=Path, required=True,
                        help="Directory containing NimbusRoman-Regular.otf and NimbusRoman-Bold.otf")
    parser.add_argument("--pdftotext", default="pdftotext")
    args = parser.parse_args()
    sources, output = args.sources.resolve(), args.output.resolve()
    if output.exists() and any(output.iterdir()):
        parser.error("--output must be a new or empty directory")
    fonts = [args.font_dir.resolve() / name for name in
             ("NimbusRoman-Regular.otf", "NimbusRoman-Bold.otf")]
    for path in fonts:
        if not path.is_file():
            parser.error(f"Missing font: {path}")
    manifest = json.loads((HERE / "data/sources.json").read_text(encoding="utf-8"))
    for source in manifest:
        path = sources / source["filename"]
        if not path.is_file() or digest(path) != source["sha256"]:
            parser.error(f"Missing source or SHA-256 mismatch: {path}")

    with TemporaryDirectory(prefix="mts-ny2022-") as temp:
        work = Path(temp)
        staged = work / "output"
        for subject in ("math", "ela"):
            (staged / subject).mkdir(parents=True)
        env = dict(os.environ, PYTHONUTF8="1", MTS_2022_SOURCES=str(sources),
                   MTS_2022_OUTPUT=str(staged), MTS_2022_WORK=str(work),
                   MTS_2022_FONT_REGULAR=str(fonts[0]), MTS_2022_FONT_BOLD=str(fonts[1]))
        for entry in manifest:
            text = work / f"{entry['subject']}-{entry['grade']}.txt"
            subprocess.run([args.pdftotext, "-layout", str(sources / entry["filename"]), str(text)],
                           check=True)
        for script in ("run_compact.py", "render_compact.py", "key.py", "check_compact.py"):
            subprocess.run([sys.executable, str(HERE / script)], env=env, check=True)
        result = []
        for entry in manifest:
            subject, grade = entry["subject"], entry["grade"]
            sub = staged / subject.lower()
            if subject == "Math":
                evidence = json.loads((sub / f"Grade-{grade}-Review.json").read_text(encoding="utf-8"))
                if [item["id"] for item in evidence["placements"]] != entry["items"]:
                    raise ValueError(f"Math grade {grade}: approved item order differs")
            prefix = f"Grade-{grade}" + ("-ELA" if subject == "ELA" else "")
            for kind in ("Student", "Teacher-Key"):
                path = sub / f"{prefix}-{kind}.pdf"
                with fitz.open(path) as pdf:
                    expected = (3 if kind == "Student" else 1) if subject == "Math" else (5 if kind == "Student" else 3)
                    if len(pdf) != expected or any(page.rect.width != 612 or page.rect.height != 792
                                                   or not page.get_text().strip() for page in pdf):
                        raise ValueError(f"Invalid page geometry or count: {path.name}")
                    result.append({"file": str(path.relative_to(staged)), "pages": len(pdf),
                                   "sha256": digest(path)})
        (staged / "artifacts.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
        import shutil
        shutil.copytree(staged, output, dirs_exist_ok=True)
    print(f"Verified {len(result)} regenerated PDFs in {output}")

if __name__ == "__main__":
    main()
