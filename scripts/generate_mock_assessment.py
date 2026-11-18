"""Independent mock-assessment CLI. Generation adapter pending; verification gate available."""
import argparse
import json
from pathlib import Path
import sys

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "src"))
from mts.products.mock_assessment.verification import evaluate, digest
from mts.infrastructure.file_system.atomic_writer import write_json

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--report", type=Path, required=True)
    parser.add_argument("--revision", required=True)
    parser.add_argument("--evidence-root", type=Path, required=True)
    parser.add_argument("--checkpoint", type=Path, required=True)
    args = parser.parse_args()
    registry = REPO / "specs/generate_mock_assessment/acceptance-criteria.json"
    result = evaluate(json.loads(registry.read_text()), json.loads(args.report.read_text()),
                      args.evidence_root, args.revision, digest(registry))
    write_json(args.checkpoint, result)
    print(result["status"])
    return 0 if result["status"] == "READY_FOR_ACCEPTANCE" else 1

if __name__ == "__main__":
    sys.exit(main())
