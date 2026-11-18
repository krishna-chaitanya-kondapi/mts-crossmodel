"""Recreate the historical workspace and execute all currently integrated profiles."""
import argparse
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STATE = ROOT / "specs/generate_mock_assessment/resume"
WORK = ROOT / "work"
OUTPUT = ROOT / "outputs"
CLI = ROOT / "scripts/generate_mock_assessment.py"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--prepare", action="store_true")
    parser.add_argument("--render", action="store_true")
    args = parser.parse_args()
    if args.prepare:
        shutil.copytree(STATE / "inputs/golden", WORK / "golden", dirs_exist_ok=True)
        WORK.mkdir(exist_ok=True)
        for path in (STATE / "inputs").glob("*manifest.json"):
            shutil.copy2(path, WORK / path.name)
        shutil.copytree(STATE / "evidence", OUTPUT, dirs_exist_ok=True)
    if args.render:
        OUTPUT.mkdir(exist_ok=True)
        for grade in (4, 5):
            subprocess.run([
                sys.executable, str(CLI), f"grade{grade}-student",
                "--source", str(WORK / f"golden/NY_Math_Grade{grade}_2024_Released_Test_Questions.pdf"),
                "--manifest", str(WORK / f"grade{grade}-student-manifest.json"),
                "--output", str(OUTPUT / f"grade{grade}-student-review.pdf"),
                "--placements", str(OUTPUT / f"grade{grade}-placements.json"),
            ], check=True, cwd=ROOT)
            subprocess.run([
                sys.executable, str(CLI), "teacher-key",
                "--manifest", str(WORK / f"grade{grade}-teacher-manifest.json"),
                "--output", str(OUTPUT / f"grade{grade}-teacher-review.pdf"),
            ], check=True, cwd=ROOT)
        subprocess.run([
            sys.executable, str(CLI), "ela-teacher",
            "--manifest", str(WORK / "ela-teacher-manifest.json"),
            "--output", str(OUTPUT / "ela-teacher-review.pdf"),
        ], check=True, cwd=ROOT)


if __name__ == "__main__":
    main()
