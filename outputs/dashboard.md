# Mock Assessment dashboard

**4 / 76 (5%) mandatory criteria verified**

**Status NOT_DONE** · Iteration 32 · audited revision `3ec9219c6fc241760e7b0d222877564a9e51e9c0`

The acceptance count is separate from the test count. V01.01 and V01.02 pass for requirements-source recovery, V01.04 for original question-paper identification, and ARCH.01 for the dedicated executable. This does not establish end-to-end generation, educational correctness, or release readiness.

| Category | Verified |
|---|---:|
| Requirements and traceability | 3 / 7 (43%) |
| Workflow and deliverables | 0 / 9 (0%) |
| Academic correctness | 0 / 7 (0%) |
| Source fidelity | 0 / 8 (0%) |
| Print and visual quality | 0 / 13 (0%) |
| Historical regression | 0 / 12 (0%) |
| Operations and repeatability | 0 / 10 (0%) |
| Architecture and isolation | 1 / 10 (10%) |

## Work completed

- Iteration 32: **40 focused tests passed**. The approved local path now embeds only rasterized crop pixels instead of original PDF page objects. Synthetic checks verified both image payloads and their order. Print and accessibility acceptance remain unverified.

- Iteration 31: **40 focused tests passed**. The local student dispatcher uses the approved PDF crop selections and order. The synthetic render displayed the two approved selections; this is not evidence that excluded source data was removed from the PDF internals.

- Iteration 30: [identified the original NYSED question papers](iteration-30-original-source-identities.txt) for all three benchmarks, with fresh local checks for Grade 4 Math and Grade 6 ELA and prior fingerprint evidence for Grade 5 Math. No source was reproduced.

- Iteration 29: **40 focused tests passed**. An approval bound to both review packet digests dispatched a synthetic renderer; missing, wrong-scope, and stale approvals did not.

- Iteration 28: **40 focused tests passed**. Preflight now validates source selections and writes a draft PDF and JSON. It rejects caller-supplied approval and leaves existing review packets unchanged.

- Iteration 27: **27 focused tests passed**. Draft RunSpec preflight validates a source digest, presence of a rights reference, blueprint counts, and student pagination inputs. It does not confer approval, verify rights, or render outputs.

- Iteration 26: verified that a fresh checkout with `core.autocrlf=false` retains all three evidence-backed passes. Previously, checkout conversion invalidated them. No additional criterion was promoted.

- Iteration 25: **22 focused Mock Assessment tests passed**. The dedicated CLI worked from outside the repository, rejected a wrong source digest without output, and accepted a UTF-8 BOM report. See [CLI evidence](iteration-25-cli-evidence.txt).

- Recovered and fingerprinted approved Mock Assessment and Math/ELA requirement sources. Weekly Practice defaults are explicitly excluded. ELA detailed requirements remain proposed/incomplete and no ELA subject design document was found.
- Latest clean full suite: **262 passed**. An earlier full-suite run had one Weekly bypass integration failure; the isolated test and clean full-suite rerun passed. The first failure's cause was not captured; test-written transaction fixtures were restored.
- Grade 4 candidate evidence records four pages, 28 ordered regions, full-width Q26, and matching page 3/4 groups and response-line counts versus the recovered golden. Page 1/2 grouping, page furniture, and question-label typography still differ; no visual-equivalence claim is made.
- Iteration 24 found copyright/permission notices in the selected NYSED sources and no source-specific authorization record in the scoped project materials. No candidate was generated in that iteration.
- No production publication occurred.

## Next steps

Next, connect the local dispatcher to an authenticated approval source and verify print and accessibility acceptance. Keep approval enforcement and full-workflow portability NOT_VERIFIED.

1. Provide written authorization, a license, or another documented rights basis covering reproduction, reformatting, local storage, and the intended distribution of the selected NYSED content.
2. While rights are pending, complete non-content criterion traceability and product-neutral architecture/synthetic-fixture checks; keep source-dependent criteria NOT_VERIFIED.
3. After authorization, build and compare the ELA candidate and repair/recompare the Grade 4 candidate.
4. Obtain qualified independent academic/source review; human approval is required before publication.

## Blockers and boundaries

- **Source rights:** blocks new source-derived ELA/Grade 4 candidate PDFs and content-parity acceptance. The ELA test credits third-party permission for a selected passage; permission for the published test does not establish MTS reuse rights. See the [rights-notice follow-up](verification-report.md#iteration-32-crop-isolation).
- **Independent review:** required for academic/source acceptance; self-review is insufficient.
- **Human publication approval:** absent, so production publication is not authorized.
- Do not use proposed Weekly ELA requirements as approved Mock Assessment policy.

[Verification report](verification-report.md) · [Machine-readable criteria](verification-report.json) · [Canonical checkpoint](../specs/generate_mock_assessment/implementation-checkpoint.json)

**Latest evidence:** [source-rights check](iteration-24-source-rights-check.json) · [requirements recovery](iteration-23-requirements-recovery.json) · [Grade 4 comparison](iteration-23-grade4-render-evidence.json) · [tests](iteration-23-tests.txt) · [open defects](iteration-23-defects.json)
