# Mock Assessment takeover

Run `python scripts/resume_mock_assessment.py` from the repository root. Read [START_HERE.md](../specs/generate_mock_assessment/resume/START_HERE.md); the canonical checkpoint owns criterion status, blockers, and next actions.

Current state: **NOT_DONE**, Iteration 23, **2 / 76 mandatory criteria PASS** for requirements-source recovery only. This is not the unit-test count and does not imply implementation or release acceptance. The audited code revision is `2c59606b7f5c9cc09069e432022d52f23f59759e`.

Latest full-suite command: `.venv\Scripts\python.exe -m pytest tests -q` (**262 passed** on the clean rerun). The initial full run had one Weekly bypass integration failure; the isolated test and clean full rerun passed. The first failure's cause was not captured. Restore test-written `data/transactions` changes after each run.

Next: (1) build the criterion-level implementation/evidence trace; (2) build and compare an ELA student candidate derived from the official PDF, including raster-only pages 10 and 16; (3) repair the recorded Grade 4 golden differences and repeat the complete comparison; (4) run both CLI production paths. Keep unsupported criteria NOT_VERIFIED. Qualified independent review is required for academic/source acceptance. Production publication requires artifact-specific human approval and remains unauthorized.

At each logical checkpoint update [the canonical checkpoint](../specs/generate_mock_assessment/implementation-checkpoint.json), evidence, verification report, and dashboard. Run `python scripts/checkpoint_mock_assessment.py`; commit and push code and state together to `master`. Large PDFs and rendered drafts stay in the development workspace.
