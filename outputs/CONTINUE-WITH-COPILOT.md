# Mock Assessment takeover

Run `python scripts/resume_mock_assessment.py` from the repository root. Read [START_HERE.md](../specs/generate_mock_assessment/resume/START_HERE.md); the canonical checkpoint owns criterion status, blockers, and next actions.

Current state: **NOT_DONE**, Iteration 30, **4 / 76 mandatory criteria PASS** for requirements-source recovery, original question-paper identification, and the dedicated executable. Audited revision `71737d500ca2bbfa07ef54894d5422596079216b`; the most recent focused suite passed 40 tests in Iteration 29. Source identity is not authorization to reproduce content.

Latest clean full-suite command: `.venv\Scripts\python.exe -m pytest tests -q` (**262 passed** at Iteration 23). The first full run had one Weekly bypass integration failure; the isolated test and clean full rerun passed. The first failure's cause was not captured. Restore test-written `data/transactions` changes after each run.

**Current blocker:** the selected NYSED ELA and Grade 4 Math source PDFs contain copyright/permission notices, and no source-specific authorization record was located in the scoped project materials. Do not generate or revise source-derived candidates until written authorization, a license, or another documented rights basis covering reproduction, reformatting, local storage, and intended distribution is recorded. See [source-rights evidence](iteration-24-source-rights-check.json).

While rights are pending, continue non-content criterion traceability and product-neutral architecture/synthetic-fixture checks; keep source-dependent criteria NOT_VERIFIED. After authorization, build and compare the ELA candidate and repair/recompare the Grade 4 candidate. Qualified independent review is required for academic/source acceptance. Production publication requires artifact-specific human approval and remains unauthorized.

Next, connect a trusted approval source and planned-run dispatcher. At each logical checkpoint update [the canonical checkpoint](../specs/generate_mock_assessment/implementation-checkpoint.json), evidence, verification report, and dashboard. Run `python scripts/checkpoint_mock_assessment.py`; commit and push to `gc-mock-assessment-implementation`, not `master`. Large PDFs and rendered drafts stay in the development workspace.
