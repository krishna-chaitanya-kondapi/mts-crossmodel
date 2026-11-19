# Generate Mock Assessment

This independent workflow implements the three source-bound historical benchmark profiles in the approved initial milestone. Read the canonical checkpoint and verification report for current acceptance status. Weekly Practice remains an independent product.

1. Restore source/golden PDFs only when needed with scripts/restore_mock_assets.py. Their fingerprints and provenance are in specs/generate_mock_assessment/golden-assets.json.
2. Run a saved fixture with scripts/generate_mock_assessment.py run --runspec <fixture.json> --source-root <sources> --output-root <review-root>. Validation binds source identity, blueprint, instructional Monday, paper and page constraints. Golden runs use local_review execution.
3. Review every item against its original source and scoring materials. Inspect every rendered page and compare the designated goldens. scripts/verify_mock_artifacts.py checks the actual selected-item inventory, official keys/credits, Math native words, bounds and page identities. scripts/compare_mock_goldens.py checks all six designated references.
4. Persist revision-bound evidence. The trusted verified-profiles.json catalog carries completed academic/source/visual reviews forward only when source, canonical manifests, implementation, renderer version, every page's pixels and review-evidence hashes match. Any mismatch remains NOT_VERIFIED and blocks release. Structural checks always execute again.
5. Evaluate all mandatory criteria using verification.evaluate, update the report/checkpoint and refresh scripts/update_mock_dashboard.py. READY_FOR_ACCEPTANCE means ready for human acceptance.
6. Production release requires a human_final_release receipt approving the exact student/key hashes, complete per-run quality evidence and the complete development gate. release targets a local destination. release-drive targets explicit PrintReady/archive folder IDs through the neutral Drive adapter. Both preserve unrelated approved artifacts and require predecessor hashes for replacement.

Run artifacts use 01-PreRun/<Monday>/<run-id> for RunSpec JSON/PDF, 02-Run for the student/key pair and 03-PostRun for runlog/review. Runtime includes measured active duration, estimates, retries and human wait. Same-run execution is locked and existing completed identities are preserved. Failed phase promotion rolls back only this run's newly created directories. Durable .attempts records permit retry accounting.

Drive publication writes an operation-tagged durable journal before mutations, stages and reads back candidates, archives predecessors under their original IDs, verifies the final set and restores the prior set on failure. A persistent outage leaves RECOVERY_REQUIRED with its journal path. After connectivity returns, use recover-release-drive --journal <trusted-journal> --credentials <authorized-user-file>. An existing lock is never stolen. After a process crash, an operator must verify its owner is inactive before clearing a stale lock. Local and Drive transport tests use temporary stores/mocks. No production release is part of the regression workflow.

Install requirements.txt and pytest in a Python environment. PyMuPDF supplies PDF rendering and is pinned to a supported major range; frozen page-review carryforward additionally requires the exact reviewed renderer version. Regenerate and re-review if the renderer changes. The lightweight resume command is read-only and requires no source PDFs or regeneration.

## Source exposure and 2022 regeneration

Before proposing a new paper, consult the [source-use ledger](../specs/generate_mock_assessment/source-use.md) and check the intended cohort against prior question and passage exposure. Record delivered and administered status after the run.

The [2022 Grades 4–6 runner](../specs/generate_mock_assessment/ny2022/README.md) regenerates the delivered Math and ELA layout from the pinned source files and explicit dependencies.
