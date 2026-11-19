# Mock Assessment takeover

Run `python scripts/resume_mock_assessment.py` from the repository root. Read [START_HERE.md](../specs/generate_mock_assessment/resume/START_HERE.md); the canonical checkpoint owns criterion status, blockers, and next actions.

Current state: **NOT_DONE**, Iteration 37, **7 / 76 mandatory criteria PASS**. Audited revision `2b695a1bac5c4668cc9f6e726ecfd445c5249050`; ARCH.04 now passes for running the tested assessment routes without Weekly curriculum or generation. Source identity is not authorization to reproduce content.

Latest clean full suite: **286 passed** in a disposable checkout at Iteration 36 with its `src` on `PYTHONPATH`. Prefer a disposable checkout to keep test-written transaction changes out of the active worktree.

**Current blocker:** the selected NYSED ELA and Grade 4 Math source PDFs contain copyright/permission notices, and no source-specific authorization record was located in the scoped project materials. Do not generate or revise source-derived candidates until written authorization, a license, or another documented rights basis covering reproduction, reformatting, local storage, and intended distribution is recorded. See [source-rights evidence](iteration-24-source-rights-check.json).

While rights are pending, continue non-content criterion traceability and product-neutral architecture/synthetic-fixture checks; keep source-dependent criteria NOT_VERIFIED. After authorization, build and compare the ELA candidate and repair/recompare the Grade 4 candidate. Qualified independent review is required for academic/source acceptance. Production publication requires artifact-specific human approval and remains unauthorized.

The [golden run inventory](../specs/generate_mock_assessment/golden-reference-inventory.md) records all three authenticated ChatGPT handoffs. Both ELA PDF digests match the existing goldens. The checked [historical benchmark targets](../specs/generate_mock_assessment/fixtures/historical-benchmark-targets.json) are comparison metadata, not runnable RunSpecs. Verify the Math chat attachment bytes and recover the remaining settings before completing the RunSpecs.

Next, connect an authorized operator issuer, provision its trusted key, and verify print and accessibility acceptance for raster crops. The dispatcher authenticates signed decisions but remains local-only. At each logical checkpoint update [the canonical checkpoint](../specs/generate_mock_assessment/implementation-checkpoint.json), evidence, verification report, and dashboard. Run `python scripts/checkpoint_mock_assessment.py`; commit and push to `gc-mock-assessment-implementation`, not `master`. Large PDFs and rendered drafts stay in the development workspace.
