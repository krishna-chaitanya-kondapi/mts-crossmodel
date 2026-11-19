# Resume Mock Assessment

Run from the repository root:

    python scripts/resume_mock_assessment.py

Read AGENTS.md, constitution.md, specs/generate_mock_assessment/implementation-checkpoint.json, definition-of-done.md, acceptance-criteria.json, and docs/software-factory/verification-driven-execution.md. Read outputs/verification-report.md and outputs/dashboard.md for human-readable state. The canonical checkpoint owns the next actions and criterion status.

Continue the existing implementation. Update the canonical checkpoint, relevant evidence, reports and dashboard after each logical milestone, then commit and push the same branch. Run python scripts/checkpoint_mock_assessment.py to validate checkpoint structure. This wrapper reads existing state and generates no worksheets.

## Current dependencies

Code lives in src/mts/products/mock_assessment and scripts/generate_mock_assessment.py. Existing tests require requirements.txt and pytest. PDF generation also requires PyMuPDF. The Iteration 23 clean full-suite rerun passed 262 tests; the initial run had one Weekly bypass integration failure that was not reproduced by an isolated test or the clean rerun. Later rendering changes need current tests.

Historical sources and references have Drive identities in outputs/historical-inventory.json and specs/generate_mock_assessment/golden-reference-inventory.md. Official Math scoring source URLs and hashes are in outputs/math-official-scoring-evidence.json. Exact source item mappings are in outputs/historical-source-item-maps.json.

Large PDFs, local drafts and scratch scripts stay in the development workspace. On a new machine retrieve necessary assets using the recorded identities and verify their hashes. Missing assets block only the dependent rendering or content checks. Do not infer PASS from missing evidence. Before reproducing or reformatting NYSED content, verify and record the rights basis; Iteration 24 found copyright/permission notices on the selected source PDFs and no source-specific authorization record in the scoped project materials.

Small renderer manifests are in specs/generate_mock_assessment/fixtures. Use explicit CLI arguments to point to local sources and output locations. ELA student generation remains an unfinished local trial; the 13-page source-control manifest is not a final candidate. Its source transcription and raster-only pages must be completed against NYSED and compared with the delivered golden.

Check a draft source-based benchmark RunSpec, optionally writing a PDF and JSON for review:

    python scripts/generate_mock_assessment.py preflight --runspec <draft.json> --source <source.pdf> --review-dir <new-review-folder>

Omit `--review-dir` for validation only. The draft requires `source.sha256`, a nonempty `source.rights_basis` reference, and `source.selection` entries with unique `source_number`, one-based `source_page`, and `type` (`multiple_choice` or `constructed_response`). Preflight checks the source PDF, selection and blueprint counts, and portrait US Letter student pagination. The packet is explicitly DRAFT; caller-provided approval or release fields are rejected. Preflight does not evaluate the referenced rights, authorize generation, or gate the existing local review renderers.

When a selection includes `bounds`, preflight checks that all four coordinates are numeric and form a nonempty rectangle inside its source page. Selections without bounds may be reviewed but cannot be rendered by the local student dispatcher.

The planned-run approval helper authenticates a separate pre-run decision with HMAC-SHA-256, checks both packet digests, then revalidates the draft against the source. The issuer signs the ASCII, sorted-key, compact JSON of `decision`, `scope`, `reviewer`, `runspec_json_sha256`, and `runspec_pdf_sha256`, prefixed by `mts/mock-assessment/pre-run/v1` and a NUL byte; the result is lowercase hex in `hmac_sha256`. The caller must provision `approval_key` from trusted configuration, never from the job or packet. The issuer must authenticate its operator and verify source rights; neither issuer nor key provisioning is wired up. This is not a release approval.

The local student dispatcher requires four PDF coordinates in `bounds` on each approved selection and accepts no separate crop manifest. It embeds raster pixels from those bounds instead of the original PDF page objects. Source text is not selectable in these crops; print and accessibility acceptance remain unverified. The dispatcher is not wired into the local review CLI or production publication. The older vector review routes still clip display rather than remove source content; do not distribute those PDFs.

## Copilot prompt

Continue Mock Assessment from the canonical checkpoint. Follow this guide and the approved Definition of Done. Implement, test and repair until all 76 mandatory criteria pass with sufficient revision-bound evidence or an external blocker prevents progress. Keep Weekly Practice independent. Persist code, evidence and exact next actions at each checkpoint. Production publication requires human approval.
