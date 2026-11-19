# Resume Mock Assessment

Run from the repository root:

    python scripts/resume_mock_assessment.py

Read AGENTS.md, constitution.md, specs/generate_mock_assessment/implementation-checkpoint.json, definition-of-done.md, acceptance-criteria.json, and docs/software-factory/verification-driven-execution.md. Read outputs/verification-report.md and outputs/dashboard.md for human-readable state. The canonical checkpoint owns the next actions and criterion status.

Continue the existing implementation. Update the canonical checkpoint, relevant evidence, reports and dashboard after each logical milestone, then commit and push the same branch. Run python scripts/checkpoint_mock_assessment.py to validate checkpoint structure. This wrapper reads existing state and generates no worksheets.

## Current dependencies

Code lives in src/mts/products/mock_assessment and scripts/generate_mock_assessment.py. Existing tests require requirements.txt and pytest. PDF generation also requires PyMuPDF. The last recorded full suite passed 248 tests. Later rendering changes need current tests.

Historical sources and references have Drive identities in outputs/historical-inventory.json and specs/generate_mock_assessment/golden-reference-inventory.md. Official Math scoring source URLs and hashes are in outputs/math-official-scoring-evidence.json. Exact source item mappings are in outputs/historical-source-item-maps.json.

Large PDFs, local drafts and scratch scripts stay in the development workspace. On a new machine retrieve necessary assets using the recorded identities and verify their hashes. Missing assets block only the dependent rendering or content checks. Do not infer PASS from missing evidence.

Small renderer manifests are in specs/generate_mock_assessment/fixtures. Use explicit CLI arguments to point to local sources and output locations. ELA student generation remains an unfinished local trial. Its implementation and source transcription must be recovered from current artifacts or completed against NYSED.

## Copilot prompt

Continue Mock Assessment from the canonical checkpoint. Follow this guide and the approved Definition of Done. Implement, test and repair until all 76 mandatory criteria pass with sufficient revision-bound evidence or an external blocker prevents progress. Keep Weekly Practice independent. Persist code, evidence and exact next actions at each checkpoint. Production publication requires human approval.
