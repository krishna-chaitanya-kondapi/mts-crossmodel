"""Isolated acceptance gate tests."""
import sys
from pathlib import Path
import tempfile
import unittest
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))
from mts.products.mock_assessment.verification import evaluate, digest

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
