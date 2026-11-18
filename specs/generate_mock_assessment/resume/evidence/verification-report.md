# Mock Assessment verification report

**NOT_DONE.** Iteration 3. All 76 mandatory criteria remain open in the verification gate.

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

Recovered the historical YPQA text into a canonical manifest and rendered it through the CLI. Two pages, twelve official letters and two labeled model responses passed structural checks. Both pages were inspected. Smaller text and punctuation fallback require repair before readability parity can pass. See the [teacher review](ela-teacher-review.md).
