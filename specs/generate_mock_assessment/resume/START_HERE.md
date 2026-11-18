# Resume Mock Assessment

From the repository root run:

    python scripts/resume_mock_assessment.py

Read AGENTS.md, constitution.md, specs/generate_mock_assessment/definition-of-done.md, acceptance-criteria.json, implementation-checkpoint.json and docs/software-factory/verification-driven-execution.md. The canonical checkpoint owns status and exact next actions. Human-readable progress is in outputs/dashboard.md and outputs/verification-report.md.

Continue the existing implementation on the same branch. Keep checkpoints, the lightweight wrapper and code together in commits and eventual merge. Run python scripts/checkpoint_mock_assessment.py after state updates. The wrapper reads checkpoint state and generates no worksheets or duplicated evidence bundles.

## Dependencies and assets

Install requirements.txt and pytest. Code is in src/mts/products/mock_assessment, shared publication primitives in src/mts/publishing and the executable entry point in scripts/generate_mock_assessment.py. Consult the canonical report for the latest test result rather than a copied count here.

Source selection and official metadata are in outputs/historical-source-item-maps.json. Official scoring URLs/fingerprints are in outputs/math-official-scoring-evidence.json and outputs/ela-official-scoring-evidence.json. Source/golden identities and pinned Git object locations are in specs/generate_mock_assessment/golden-assets.json. Restore only the assets needed:

    python scripts/restore_mock_assets.py --kind source --destination work/golden
    python scripts/restore_mock_assets.py --kind golden --destination work/golden

A shallow clone may need the exact fetch printed by the helper. No duplicate input snapshot is maintained in the current tree. The user selected the recovered ELA Drive pair as golden. Original ChatGPT Library byte identity remains unknown; this selection grants no production approval.

## Execute and verify

    python scripts/generate_mock_assessment.py run --runspec specs/generate_mock_assessment/fixtures/ny2025_ela_grade6-runspec.json --source-root work/golden --output-root work/review

Use the analogous ny2024_math_grade4 and ny2024_math_grade5 RunSpecs. Outputs follow phase/Monday/run-ID conventions. Complete identities are preserved; use a different output root for repeat runs. Runtime, hashes, placements, retry accounting and quality status are logged. Golden runs never publish.

    python scripts/verify_mock_artifacts.py --run-root work/review --source-root work/golden --output work/artifact-audit.json
    python scripts/compare_mock_goldens.py --run-root work/review --golden-root work/golden --output work/golden-comparison.json
    python -m pytest tests -q

Use tests/ as the maintained suite root. Bare pytest also collects archived duplicate tests and obsolete local scratch scripts. Some existing Weekly Practice tests mutate tracked data/transactions fixtures; inspect and restore only test-owned changes before committing.

verified-profiles.json carries completed reviews forward only for exact source, canonical manifest, normalized implementation, renderer and page-pixel matches with all review evidence intact. Changed/unknown artifacts require a fresh independent academic/source/every-page review. Missing evidence is never PASS. Full review closure and all differences are documented in outputs/iteration-27-review-closure.md and the associated audits.

## Release boundary

No final human release receipt or production publication has been performed. A completed development gate is READY_FOR_ACCEPTANCE. release/release-drive additionally require per-run quality PASS and explicit human approval of both exact PDF hashes. Drive rollback/recovery and unrelated-file preservation are tested with mocked transport. See workflows/generate-mock-assessment.md for durable journal recovery. Never fabricate an approval or infer it from golden selection.

## Copilot takeover prompt

Continue Mock Assessment from the canonical checkpoint on this branch. Read this guide and the approved Definition of Done. Execute the exact next actions, repair and reverify until all 76 mandatory criteria pass with sufficient revision-bound evidence or a genuine external blocker prevents progress. Keep Weekly Practice independent. Reuse existing implementation, golden assets and evidence. Persist code, report/dashboard, defects and exact next actions at each logical checkpoint. Keep the lightweight takeover files with those checkpoints. Production publication requires explicit human approval.
