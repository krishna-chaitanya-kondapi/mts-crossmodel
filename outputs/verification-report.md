# Mock Assessment verification report

**NOT_DONE. Iteration 31.** The revision-bound gate records **4 / 76 mandatory criteria PASS**; 72 remain open. V01.01 and V01.02 pass for requirements-source recovery, V01.04 for original question-paper identification, and ARCH.01 for the dedicated executable. This acceptance count is not the unit-test count and does not claim end-to-end implementation, academic correctness, or release readiness.

## Historical evidence

- Grade 4 Math, NYSED 2024. Recovered the staged review worksheet and key from Drive and verified their four-page and one-page counts. The handoff calls out 29 items and 10 constructed responses. The listed IDs, official item map, and staged key show 28 items, with 19 multiple-choice and 9 constructed-response items. The official item map is PDF page 34.
- Grade 5 Math, NYSED 2024. The official item map on PDF page 32 confirms the handoff's selection of 28 items, with 19 multiple-choice and 9 constructed responses. The historical handoff records a Q40 correction to 35 tiles and 8 3/4 square feet.
- Grade 6 ELA, NYSED 2025. The official item map on PDF page 43 confirms Q8–14 and Q22–28, with 12 multiple-choice and two 2-credit constructed responses. The handoff identifies the final delivered Library PDFs. The Drive copies match the reported titles and page counts. Byte identity with the Library PDFs remains unverified. The handoff records excess trailing whitespace on student pages 1 and 3.
- The handoffs document delivery for Grade 5 Math and Grade 6 ELA and staging for Grade 4 Math. Artifact-specific final approval remains unverified.

## Implementation and verification

Added an independent NYSED item-map reader with checks for missing rows, duplicates, and inconsistent answer keys. Ran it against each historical original source PDF. The resulting JSON records all 70 selected items, their source and output numbers, official keys, points, standards, source hashes, and item-map pages. This is source scoring evidence. Independent academic review, source-region validation, rendering, and historical regression remain pending. There were no production publications.

See the JSON and checkpoint for the remaining criteria and next actions.

All 248 tests passed, including Weekly Practice and five new item-map tests. Test-written transaction fixtures were restored.

## Iteration 4

Added hash-bound vector crop rendering and trialed all 28 Grade 5 source regions. The trial placed 28 regions on 14 Letter pages at 75% whole-crop scale. The capped run rejected output at the four-page ceiling. This is a failed layout experiment, with no accepted regenerated worksheet or teacher key. Full-region crops retain source whitespace and need to be replaced with component-level packing. Bounds and placements are persisted for repair. The test count above applies to iteration 3.

## Iteration 5

Added forward two-column placement for narrow regions and a full-width fallback. A synthetic layout check confirms that the right column starts below a preceding full-width region. The real Grade 5 whole-crop replay remained at 14 pages, so no pagination criterion moved to PASS. The dashboard now calculates category percentages from mandatory criterion statuses.

## Iteration 6

The component trial reduced Grade 5 from 14 pages to eight and still exceeded the four-page ceiling. Inspection of the historical PDF confirmed typeset 9.2 pt prompts, 9 pt choices and embedded vector figures. Use that architecture for the next attempt. See [historical implementation audit](grade5-historical-implementation-audit.md).

## Iteration 7

Grade 5 measured reflow placed 28 ordered question blocks on three Letter pages. Structural checks passed. Source extraction omits some vector notation, and the draft figure bounds and response regions require review. Evidence is in [the reflow trial record](grade5-reflow-evidence.json). The draft PDF remains in the working directory and is not a release candidate.

## Iteration 8

Changed the diagnostic renderer to crop vector-only choice lines from the official source. The trial produced four Letter pages with 28 ordered placements, no overlapping measured blocks, and no placeholder strings. Visual crop coverage and mixed-text formula fidelity remain unverified. Source equivalence and independent academic QA are still open.

### Iteration 8 visual findings

Reviewed all four diagnostic renders. Source-fidelity defects remain visible. Q2, Q7, Q10, Q27, Q28, Q30, Q32, Q34, Q37, Q40, Q41 and Q42 show missing mathematical notation in stems or standalone expressions. Q33 visibly lacks its fourth choice. Q43's key is clipped at the right edge. The printed response labels are missing from several constructed-response items. Treat these as blocking defects despite the successful page-count and placement checks.

## Iteration 9

Restored missing formulas, the fourth Q33 choice, response labels, and the clipped Q43 key. The repaired four-page Grade 5 trial passed six targeted text assertions. All four images were inspected. [Scoring review](grade5-scoring-review.md) records worked answers to all 28 items. Full original-to-output comparison, rubric review and a separate rendered teacher key remain open.

## Iteration 10

The dedicated CLI rendered a one-page Grade 5 teacher key. Automated checks confirmed 19 official multiple-choice answers and nine constructed-response numbers and credit values. The page was visually inspected. Official rubric alignment requires separate verification. The full existing suite passed 248 tests, including Weekly Practice, and test-written transaction fixtures were restored.

## Iteration 11

The Grade 5 student reflow and teacher key ran through the product CLI. The comparison fingerprints both generated PDFs and both final delivered golden PDFs. The student output met the four-page ceiling but used four pages against three historically. The key matched the historical one-page count. This comparison does not establish academic or visual equivalence.

## Iteration 12

Typeset the 36 source-vector choices as compact text, preserving the five original figure crops. Grade 5 now matches the delivered golden page counts at three student pages and one key page. The three student pages were inspected. The generated layout uses slash fractions and different placements from the delivered golden. Full original-source fidelity and official rubric review remain open.

## Iteration 13

Recovered and fingerprinted official NYSED scoring materials for Grade 4 and Grade 5, and indexed their 18 constructed-response exemplars. Generated and visually inspected the one-page Grade 4 teacher key. It matches the staged key's page count and contains all 19 official answer labels and nine constructed responses with credits. Full academic rubric comparison and the Grade 4 student worksheet remain open.

## Iteration 14

Compared all nine Grade 5 worked solutions to the visible official full-credit exemplars. All nine agree. See the [scoring review](grade5-scoring-review.md) for exact source pages and results. Partial-credit guidance is absent from the current key.

## Iteration 15

Compared all 28 Grade 5 question regions against the NYSED original. Visually checked 13 restored notation cases. Restored three response rules per item on Q41–43 and verified the updated PDF remains three pages. See the [source comparison](grade5-source-comparison.md). Figure clearance and print-size writing space remain open.

## Iteration 16

Increased Q41–43 writing-line spacing from 8 pt to 12 pt and reallocated blank work space. The worksheet still fits three pages. Measured all five figure crop clearances. See the [print review](grade5-print-layout-review.md).

## Iteration 17

The initial Grade 4 source crop trial found all 28 items but used nine pages. The page ceiling correctly rejected it. Compared all nine Grade 4 full-credit exemplar pages. Corrected the review key to accept 68–78 degrees for Q36 and either right or isosceles triangles for Q38. The corrected key was verified to remain one page and visually inspected. Partial-credit policy and student reflow remain open.

## Iteration 18

Grade 4 compact reflow reduced the source-based student trial from nine pages to four, matching the staged reference. Q26 stayed full width with all four vector choices. Initial visual inspection identified partially clipped formulas in Q2 and Q22, a clipped figure in Q31, and missing operands in Q34. The draft was repaired and structurally rechecked. The complete repaired-page visual and fidelity review remains open.

## Iteration 19

Integrated the source-bound Grade 4 profile into the CLI. Verified four Letter pages, 28 ordered items, 76 choice labels, full-width Q26 and clearance above 6 pt for all nine tested crops. Measurement used a two-pixels-per-point grayscale render, threshold 180/255, and the intended output scale. Reviewed the repaired layout. The fourth page contains only Q44, so page utilization and full academic and source fidelity remain open.

## Iteration 20

Mapped ELA passages to source pages 9–11 and 15–17, and the questions to source pages 12–14 and 18–21. The draft fits four pages, retains the source cipher image and includes five lines for each constructed response. It uses the delivered worksheet's passage transcription as an intermediate input, including text corresponding to image-only source pages 10 and 16. Full source review, independent academic checks, CLI integration, and the ELA teacher key remain open.

## Iteration 21

Recovered the historical YPQA text into a canonical manifest and rendered it through the CLI. Two pages, twelve official letters and two labeled model responses passed structural checks. Both pages were inspected. Smaller text and punctuation fallback required repair before readability parity could pass. See the [teacher review](ela-teacher-review.md).

## Iteration 22

Installed the declared PyMuPDF dependency into the selected `.venv` and confirmed Pylance resolves `pymupdf` there. The complete suite passed: 257 tests. The suite rewrote tracked Weekly Practice transaction fixtures; those test side effects were restored. See [test output](iteration-22-tests.txt).

Repaired ELA teacher-key typography and punctuation fallback. The two-page candidate contains all twelve official multiple-choice answers and both labeled MTS model responses; its SHA-256 is `208ecc4a93d4f41e38f030617322f6b98b35eee7cf01f7e066d40f3c7a0b5c51`. Its answers match the two-page historical key text. Equivalent print readability, independent answer prediction, and rubric alignment remain NOT_VERIFIED.

Added an ELA student CLI route through the hash-bound source renderer and a synthetic-manifest route test. This does not establish a source-faithful ELA student output: an official-source-derived manifest and comparison of passages, questions, choices, figures, and instructions remain missing.

Applied the Grade 4 Q42 page break. The candidate is four pages with 28 ordered regions, full-width Q26, and Q42–44 on page four; SHA-256 `faac0cbaf4b9d4cebee4843181c76a4d59b68ae09847f1a917ef689e707f8dd3`. The one-page teacher-key candidate has SHA-256 `fc8d015bacc65ead68c01b831a0bd62890f53dd35a4b06683eae65c622e949bd`. Both candidates were visually inspected. These are local review artifacts under `%TEMP%\\mock-assessment-iteration22`; actual paths, source identities, and structural checks are in [iteration 22 render evidence](iteration-22-render-evidence.json). Independent academic/source-fidelity review, historical student-golden comparison, and acceptance of fourth-page utilization remain open.

No acceptance criterion is promoted: **0 / 76 mandatory criteria verified**. No production publication occurred. The checkpoint remains NOT_DONE; historical approval, independent review, source fidelity, and broad end-to-end workflow evidence are unresolved.

## Iteration 23

Recovered and fingerprinted the approved Mock Assessment contract and the Math and ELA requirements sources. V01.01 and V01.02 now pass for **source recovery and authority/scope classification only**. The ELA detailed requirements remain proposed/incomplete and no ELA subject design document was found; Weekly Practice rules and defaults were not imported as Mock Assessment policy. See [requirements recovery evidence](iteration-23-requirements-recovery.json).

The full suite passed **262 tests** on the clean rerun. The first full run had 261 passed and one Weekly bypass integration failure; the isolated test passed, then the clean full rerun passed. The first failure's cause was not captured. Test-written transaction fixtures were restored. See [Iteration 23 test output](iteration-23-tests.txt).

Compared the Grade 4 candidate with the recovered four-page historical golden. The candidate has 28 ordered items, full-width Q26, matching page 3/4 item groups, and matching response-line counts. It still differs in page 1/2 item grouping, all-page branding/numbering/student fields, and boxed question-label typography. No visual or academic equivalence is claimed. See [Grade 4 render evidence](iteration-23-grade4-render-evidence.json) and [open defects](iteration-23-defects.json).

The source-control ELA manifest is not a final candidate. All other mandatory criteria remain NOT_VERIFIED. Next: complete criterion-level traceability, build an ELA candidate from the official source (including raster-only pages 10 and 16), repair the recorded Grade 4 golden differences, and run production-path verification. Qualified independent review is needed for academic/source acceptance; artifact-specific human approval remains required before production publication.

## Iteration 24: source-rights blocker

Before creating another source-derived candidate, checked PDF metadata and rights-notice indicators without extracting or recording assessment text. The selected ELA PDF has copyright/permission notices on pages 7 and 24; the Grade 4 Math source has copyright notices on pages 5 and 19; its scoring source has one on page 2. No source-specific authorization record was located in the scoped project materials. No candidate PDF was generated in this iteration. See [source-rights check](iteration-24-source-rights-check.json).

**Needed to unblock source-derived work:** written authorization, a license, or another documented rights basis covering reproduction, reformatting, local storage, and the intended distribution of these selected materials. Without it, ELA candidate generation and Grade 4 source-derived repairs/content-parity evidence are blocked; related source-dependent criteria remain NOT_VERIFIED. Non-content traceability and synthetic-fixture/architecture checks can continue. This is not a legal determination. Qualified independent academic review and artifact-specific human publication approval remain separate requirements.

## Iteration 25: standalone CLI

The [CLI integration evidence](iteration-25-cli-evidence.txt) verifies ARCH.01. The entry point ran from a temporary working directory, rendered and checked a synthetic PDF, rejected a wrong source digest without output, and persisted `NOT_DONE` after reading a UTF-8 BOM report missing criterion evidence. All 22 focused tests passed. No historical candidate was generated or published.

## Iteration 26: checkout-stable gate evidence

The same report and audited revision produced **0/76 PASS** in a fresh checkout of `f68fc18` with `core.autocrlf=false` and **3/76 PASS** in a fresh checkout of `55ea8c1` with the same setting. Git attributes now preserve the existing registry and report-evidence checkout bytes. Hashing and PDF identity checks are unchanged. The gate remains `NOT_DONE` and V07.09 stays NOT_VERIFIED because this test did not cover full workflow portability. Next: implement and test synthetic RunSpec preflight and record the criterion trace.

## Iteration 27: draft RunSpec preflight

The [preflight integration tests](../tests/mock_assessment/test_preflight.py) passed a valid synthetic draft and rejected missing rights information, a mismatched source digest, inconsistent item counts, and a Boolean page count. All **27 focused Mock Assessment tests passed**. This is partial evidence for V02.06, V02.10, and V07.05; none moves to PASS. The preflight does not validate rights documentation, generate a RunSpec PDF/JSON pair, or enforce approval in the renderers. No historical candidate was generated or published.

## Iteration 28: RunSpec review packet

The [synthetic CLI tests](../tests/mock_assessment/test_preflight.py) verified selection pages, unique source question numbers, item format counts, and a draft PDF/JSON pair. The CLI rejected caller-supplied approval and did not overwrite existing packets. **40 focused tests passed.** The bundle still cannot authorize generation; full RunSpec and approval criteria remain NOT_VERIFIED. No historical assessment was generated or published.

## Iteration 29: digest-bound pre-run approval

The [approval helper](../src/mts/products/mock_assessment/approval.py) revalidates the draft and source before dispatch. The synthetic integration test verified that missing, release-scoped, or stale decisions prevented rendering and that a matching pre-run decision dispatched the test renderer. **40 focused tests passed.** No new criteria pass: a trusted approval source and real planned-run dispatch are not connected, and no historical assessment was generated or published.

## Iteration 30: original-source identification

[Source identity evidence](iteration-30-original-source-identities.txt) verifies V01.04 for the original NYSED question papers. The Grade 4 and ELA PDFs were rehashed locally and their publisher metadata checked. The Grade 5 fingerprint was matched across prior inventory, item-map, and renderer records; that PDF was not reacquired in this iteration. No generated artifacts, rights authorization, or fidelity claims result from this check.

## Iteration 31: approved-input local dispatch

The local dispatcher renders only the selected bounds in the approved order on the visible page, without accepting a second manifest. The synthetic test also verified stale approval rejection and output preservation. **40 focused tests passed.** The existing vector crop method is not redaction; distribution requires verifying or replacing it to exclude hidden source data. Authentication, rights, and full approval enforcement remain NOT_VERIFIED.
