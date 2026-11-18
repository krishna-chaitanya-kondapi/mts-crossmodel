"""Collect objective source identity and isolation evidence for a checkpoint review."""
import ast
from hashlib import sha256
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from mts.products.mock_assessment.verification import digest


def main():
    sources = json.loads((ROOT / "outputs/historical-source-item-maps.json").read_text())
    verified = []
    for record in sources:
        source = ROOT / "work/golden" / record["source_filename"]
        if not source.is_file() or digest(source) != record["source_sha256"]:
            raise SystemExit(f"Missing or mismatched source: {source.name}")
        verified.append({
            "run_id": record["run_id"], "filename": source.name,
            "sha256": digest(source), "selected_items": len(record["items"]),
        })
    entry = ROOT / "scripts/generate_mock_assessment.py"
    files = [entry, *sorted((ROOT / "src/mts/products/mock_assessment").glob("*.py"))]
    imports = []
    for path in files:
        for node in ast.walk(ast.parse(path.read_text(encoding="utf-8-sig"))):
            if isinstance(node, ast.ImportFrom):
                imports.append(node.module or "")
            elif isinstance(node, ast.Import):
                imports.extend(alias.name for alias in node.names)
    prohibited = [name for name in imports if "weekly" in name or "curriculum" in name or "subjects" in name]
    if prohibited:
        raise SystemExit(f"Unexpected product dependencies: {prohibited}")
    result = subprocess.run([sys.executable, str(entry), "--help"], cwd=ROOT,
                            capture_output=True, text=True, check=True)
    changed = subprocess.check_output(
        ["git", "diff", "--name-only", "52bac0bfbbb27cb87037f4123ad86fb8b9ba16da", "HEAD"],
        cwd=ROOT, text=True).splitlines()
    weekly_changes = [p for p in changed if p.startswith(("src/mts/subjects/", "data/config/subjects/"))]
    if weekly_changes:
        raise SystemExit(f"Weekly implementation changes: {weekly_changes}")
    report = {
        "revision": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
        "source_checks": verified, "imports_reviewed": sorted(set(imports)),
        "prohibited_imports": prohibited, "weekly_implementation_changes": weekly_changes,
        "cli_help_returncode": result.returncode,
        "implementation_hashes": {p.relative_to(ROOT).as_posix(): digest(p) for p in files},
        "limitations": [
            "Import review and help invocation establish entry point and dependency isolation.",
            "They do not establish complete orchestration, ELA source fidelity or academic correctness.",
        ],
    }
    destination = ROOT / "outputs/iteration-23-audit.json"
    destination.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(f"Verified {len(verified)} original source identities, isolated imports and standalone CLI")


if __name__ == "__main__":
    main()