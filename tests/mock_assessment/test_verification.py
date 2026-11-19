"""Isolated acceptance gate tests."""
import json
import subprocess
import sys
from pathlib import Path
import tempfile
import unittest
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))
from mts.products.mock_assessment.verification import evaluate, digest


def test_cli_reads_utf8_report_and_persists_not_done(tmp_path):
    repo = Path(__file__).resolve().parents[2]
    registry = repo / "specs" / "generate_mock_assessment" / "acceptance-criteria.json"
    report = tmp_path / "report.json"
    report.write_text(json.dumps({
        "revision": "review",
        "registry_sha256": digest(registry),
        "criteria": [],
    }), encoding="utf-8-sig")
    checkpoint = tmp_path / "checkpoint.json"

    result = subprocess.run([
        sys.executable, str(repo / "scripts" / "generate_mock_assessment.py"),
        "--report", str(report), "--revision", "review",
        "--evidence-root", str(tmp_path), "--checkpoint", str(checkpoint),
    ], cwd=tmp_path, capture_output=True, text=True)

    assert result.returncode == 1, result.stderr
    assert result.stdout.strip() == "NOT_DONE"
    assert json.loads(checkpoint.read_text(encoding="utf-8"))["status"] == "NOT_DONE"


class VerificationTests(unittest.TestCase):
    def test_gate(self):
        registry = {"criteria": [{"id": "X", "mandatory": True}]}
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp) / "evidence.txt"
            p.write_text("review evidence")
            report = {"revision": "r", "registry_sha256": "h", "criteria": [
                {"id": "X", "status": "PASS", "method": "review", "reviewer": "test",
                 "expected": "x", "actual": "x", "evidence": [{"path": p.name, "sha256": digest(p)}]}]}
            self.assertEqual(evaluate(registry, report, tmp, "r", "h")["status"], "READY_FOR_ACCEPTANCE")
            self.assertEqual(evaluate(registry, report, tmp, "other", "h")["status"], "NOT_DONE")
            p.write_text("changed")
            self.assertEqual(evaluate(registry, report, tmp, "r", "h")["status"], "NOT_DONE")
            report["criteria"][0]["status"] = "WAIVED"
            self.assertEqual(evaluate(registry, report, tmp, "r", "h")["status"], "NOT_DONE")
            report["criteria"] = []
            self.assertEqual(evaluate(registry, report, tmp, "r", "h")["status"], "NOT_DONE")

if __name__ == "__main__":
    unittest.main()
