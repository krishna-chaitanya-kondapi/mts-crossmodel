"""Restore selected hash-verified benchmark assets from pinned Git history on demand."""

import argparse
from hashlib import sha256
import json
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--kind", choices=["source", "golden", "all"], default="source")
    parser.add_argument("--destination", type=Path, required=True)
    args = parser.parse_args()
    registry = json.loads(
        (ROOT / "specs/generate_mock_assessment/golden-assets.json").read_text()
    )
    assets = [
        item
        for item in registry["assets"]
        if args.kind == "all" or item["kind"] == args.kind
    ]
    args.destination.mkdir(parents=True, exist_ok=True)
    for item in assets:
        target = args.destination / item["filename"]
        if (
            target.is_file()
            and sha256(target.read_bytes()).hexdigest() == item["sha256"]
        ):
            print(f"Verified cached {target.name}")
            continue
        try:
            data = subprocess.check_output(
                ["git", "show", f'{item["git_commit"]}:{item["git_path"]}'],
                cwd=ROOT,
                stderr=subprocess.DEVNULL,
            )
        except subprocess.CalledProcessError as error:
            raise SystemExit(
                f'Asset commit unavailable. Fetch it with git fetch origin {item["git_commit"]}, then retry.'
            ) from error
        if sha256(data).hexdigest() != item["sha256"]:
            raise SystemExit(f"Archived asset fingerprint mismatch: {target.name}")
        temporary = target.with_suffix(target.suffix + ".restore")
        temporary.write_bytes(data)
        temporary.replace(target)
        print(f"Restored verified {target.name}")


if __name__ == "__main__":
    main()
