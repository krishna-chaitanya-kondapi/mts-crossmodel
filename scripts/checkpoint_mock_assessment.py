"""Refresh the repository-contained takeover state and fingerprint its dependencies."""
import argparse
from hashlib import sha256
import json
from pathlib import Path
import shutil
import subprocess

ROOT = Path(__file__).resolve().parents[1]
STATE = ROOT / "specs/generate_mock_assessment/resume"


def fingerprint(path):
    content = path.read_bytes()
    if path.suffix in {".py", ".md", ".json", ".txt", ".ps1"}:
        content = content.replace(b"\r\n", b"\n")
    return sha256(content).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--verify", action="store_true")
    args = parser.parse_args()
    inventory_path = STATE / "inventory.json"
    if args.verify:
        inventory = json.loads(inventory_path.read_text(encoding="utf-8"))
        failures = [
            row["path"] for row in inventory["files"]
            if not (ROOT / row["path"]).is_file()
            or fingerprint(ROOT / row["path"]) != row["sha256"]
        ]
        if failures:
            raise SystemExit("Checkpoint files missing or changed: " + ", ".join(failures))
        print(f"Verified {len(inventory['files'])} takeover files")
        return

    evidence = STATE / "evidence"
    evidence.mkdir(parents=True, exist_ok=True)
    for path in (ROOT / "outputs").glob("*"):
        if path.is_file() and path.suffix in {".json", ".md", ".txt", ".pdf"}:
            shutil.copy2(path, evidence / path.name)
    for path in (ROOT / "work").glob("*manifest.json"):
        shutil.copy2(path, STATE / "inputs" / path.name)
    shutil.copy2(ROOT / "specs/generate_mock_assessment/implementation-checkpoint.json",
                 evidence / "implementation-checkpoint.json")
    paths = list(STATE.rglob("*"))
    paths += list((ROOT / "src/mts/products/mock_assessment").glob("*.py"))
    paths += [ROOT / "scripts/generate_mock_assessment.py", ROOT / "scripts/resume_mock_assessment.py",
              Path(__file__), ROOT / "specs/generate_mock_assessment/implementation-checkpoint.json"]
    files = [
        {"path": path.relative_to(ROOT).as_posix(), "sha256": fingerprint(path)}
        for path in sorted(set(paths))
        if path.is_file() and path != inventory_path and "__pycache__" not in path.parts
    ]
    inventory = {
        "status": "NOT_DONE",
        "hash_policy": "SHA256, CRLF normalized to LF for code and text files",
        "base_revision": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
        "revision_note": "Base revision precedes the checkpoint commit. File hashes identify this snapshot.",
        "files": files,
    }
    inventory_path.write_text(json.dumps(inventory, indent=2) + "\n", encoding="utf-8")
    print(f"Recorded {len(files)} takeover files")


if __name__ == "__main__":
    main()