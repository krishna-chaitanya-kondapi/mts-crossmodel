# Mock Assessment dashboard

**3 / 76 (4%) mandatory criteria verified**

**Status NOT_DONE** · Iteration 28 · audited code revision `271d36adb580176eb112bef51550b39e2e9253ba`

The acceptance count is separate from the test count. V01.01 and V01.02 pass for requirements-source recovery; ARCH.01 passes for the dedicated executable. This does not establish end-to-end generation, educational correctness, or release readiness.

| Category | Verified |
|---|---:|
| Requirements and traceability | 2 / 7 (29%) |
| Workflow and deliverables | 0 / 9 (0%) |
| Academic correctness | 0 / 7 (0%) |
| Source fidelity | 0 / 8 (0%) |
| Print and visual quality | 0 / 13 (0%) |
| Historical regression | 0 / 12 (0%) |
| Operations and repeatability | 0 / 10 (0%) |
| Architecture and isolation | 1 / 10 (10%) |

## Work completed

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

Next, test a separate approval record bound to the exact draft PDF and JSON digests, including rejection of stale approvals. Keep full-workflow portability NOT_VERIFIED.

1. Provide written authorization, a license, or another documented rights basis covering reproduction, reformatting, local storage, and the intended distribution of the selected NYSED content.
2. While rights are pending, complete non-content criterion traceability and product-neutral architecture/synthetic-fixture checks; keep source-dependent criteria NOT_VERIFIED.
3. After authorization, build and compare the ELA candidate and repair/recompare the Grade 4 candidate.
4. Obtain qualified independent academic/source review; human approval is required before publication.

## Blockers and boundaries

- **Source rights:** blocks new source-derived ELA/Grade 4 candidate PDFs and content-parity acceptance until authorization is documented. This is not a legal determination.
- **Independent review:** required for academic/source acceptance; self-review is insufficient.
- **Human publication approval:** absent, so production publication is not authorized.
- Do not use proposed Weekly ELA requirements as approved Mock Assessment policy.

[Verification report](verification-report.md) · [Machine-readable criteria](verification-report.json) · [Canonical checkpoint](../specs/generate_mock_assessment/implementation-checkpoint.json)

**Latest evidence:** [source-rights check](iteration-24-source-rights-check.json) · [requirements recovery](iteration-23-requirements-recovery.json) · [Grade 4 comparison](iteration-23-grade4-render-evidence.json) · [tests](iteration-23-tests.txt) · [open defects](iteration-23-defects.json)
