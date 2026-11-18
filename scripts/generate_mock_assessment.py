"""Independent mock-assessment verification and local PDF CLI."""
import argparse
import json
from pathlib import Path
import sys

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "src"))
from mts.products.mock_assessment.verification import evaluate, digest
from mts.products.mock_assessment.teacher_key import render_teacher_key
from mts.infrastructure.file_system.atomic_writer import write_json

def main():
    if len(sys.argv) > 1 and sys.argv[1] == "ela-student":
        from mts.products.mock_assessment.source_render import render_student

        parser = argparse.ArgumentParser(description="Render a source-bound ELA student PDF")
        parser.add_argument("--source", type=Path, required=True)
        parser.add_argument("--manifest", type=Path, required=True)
        parser.add_argument("--output", type=Path, required=True)
        parser.add_argument("--placements", type=Path, required=True)
        args = parser.parse_args(sys.argv[2:])
        manifest = json.loads(args.manifest.read_text(encoding="utf-8-sig"))
        placements = render_student(args.source, manifest, args.output)
        write_json(args.placements, {"placements": placements})
        return 0

    if len(sys.argv) > 1 and sys.argv[1] == "ela-teacher":
        from mts.products.mock_assessment.ela_teacher import render_ela_teacher

        parser = argparse.ArgumentParser(description="Render the historical ELA YPQA review key")
        parser.add_argument("--manifest", type=Path, required=True)
        parser.add_argument("--output", type=Path, required=True)
        args = parser.parse_args(sys.argv[2:])
        manifest = json.loads(args.manifest.read_text(encoding="utf-8-sig"))
        render_ela_teacher(manifest, args.output)
        return 0

    if len(sys.argv) > 1 and sys.argv[1] in {"grade4-student", "grade5-student"}:
        if sys.argv[1] == "grade4-student":
            from mts.products.mock_assessment.grade4_student import render_grade4_student as render_student
        else:
            from mts.products.mock_assessment.grade5_student import render_grade5_student as render_student

        parser = argparse.ArgumentParser(description="Render the historical Math review worksheet")
        parser.add_argument("--source", type=Path, required=True)
        parser.add_argument("--manifest", type=Path, required=True)
        parser.add_argument("--output", type=Path, required=True)
        parser.add_argument("--placements", type=Path, required=True)
        args = parser.parse_args(sys.argv[2:])
        manifest = json.loads(args.manifest.read_text(encoding="utf-8-sig"))
        placements = render_student(args.source, manifest, args.output)
        write_json(args.placements, {"placements": placements})
        return 0

    if len(sys.argv) > 1 and sys.argv[1] == "teacher-key":
        parser = argparse.ArgumentParser(description="Render a local Math teacher key")
        parser.add_argument("--manifest", type=Path, required=True)
        parser.add_argument("--output", type=Path, required=True)
        args = parser.parse_args(sys.argv[2:])
        manifest = json.loads(args.manifest.read_text(encoding="utf-8-sig"))
        render_teacher_key(manifest["items"], manifest["solutions"], args.output, title=manifest["title"])
        return 0

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
