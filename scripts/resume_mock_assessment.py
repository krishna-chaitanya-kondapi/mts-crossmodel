"""Show the current Mock Assessment checkpoint without mutating or generating artifacts."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CHECKPOINT = ROOT / "specs/generate_mock_assessment/implementation-checkpoint.json"


def main():
    state = json.loads(CHECKPOINT.read_text(encoding="utf-8-sig"))
    print(f"Status: {state['status']} | iteration {state['iteration']}")
    print("Read specs/generate_mock_assessment/resume/START_HERE.md")
    print("\nNext actions:")
    for action in state.get("next", []):
        print(f"- {action}")
    missing = [path for path in state.get("evidence", []) if not (ROOT / path).is_file()]
    print(f"\nEvidence paths: {len(state.get('evidence', []))}; unavailable locally: {len(missing)}")
    for path in missing:
        print(f"- {path}")
    print("\nRead outputs/verification-report.md and outputs/dashboard.md for current findings.")


if __name__ == "__main__":
    main()