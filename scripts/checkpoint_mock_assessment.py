"""Validate the canonical Mock Assessment checkpoint without copying artifacts."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main():
    spec = ROOT / "specs/generate_mock_assessment"
    state = json.loads((spec / "implementation-checkpoint.json").read_text(encoding="utf-8-sig"))
    registry = json.loads((spec / "acceptance-criteria.json").read_text(encoding="utf-8-sig"))
    required = {row["id"] for row in registry["criteria"]}
    ids = [row["id"] for row in state["criteria"]]
    if len(ids) != len(set(ids)) or set(ids) != required:
        raise SystemExit("Checkpoint criteria differ from the acceptance registry")
    if not state.get("next"):
        raise SystemExit("Checkpoint needs exact next actions")
    if state["status"] != "NOT_DONE":
        raise SystemExit("Completion requires the full revision-bound verification gate")
    print(f"Valid checkpoint: iteration {state['iteration']}, {len(ids)} criteria")
    print("Commit the canonical checkpoint, changed code, and relevant evidence together.")


if __name__ == "__main__":
    main()