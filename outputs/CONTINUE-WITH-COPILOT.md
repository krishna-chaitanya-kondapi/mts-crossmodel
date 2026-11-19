# Mock Assessment takeover

Run `python scripts/resume_mock_assessment.py` from the repository root. It reads the canonical checkpoint and lists the next actions. Follow [START_HERE.md](../specs/generate_mock_assessment/resume/START_HERE.md).

At each logical checkpoint update [implementation-checkpoint.json](../specs/generate_mock_assessment/implementation-checkpoint.json), relevant evidence and the Markdown dashboard, commit the changed files and push the same branch. Validate the checkpoint with `python scripts/checkpoint_mock_assessment.py`. Do not promote unsupported acceptance criteria.

The latest full test command is `.venv\Scripts\python.exe -m pytest tests -q` (257 passed at iteration 22); restore test-written `data/transactions` changes after the run. PyMuPDF is declared in requirements.txt and installed in the selected `.venv`.

The current implementation remains NOT_DONE (0 / 76 mandatory criteria verified). Next actions: create and verify the source-derived ELA student manifest against the delivered golden, complete Grade 4 academic/source review and historical-golden comparison, then run and record production-path checks. Large PDFs and rendered drafts stay in the development workspace; no snapshot copying is required to transfer control. Production publication requires human approval.
