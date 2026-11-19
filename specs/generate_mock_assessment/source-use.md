# Mock Assessment source-use ledger

Consult this ledger before proposing a paper. A row records what is known about use. A prepared packet or internal regression alone does not establish that students saw the questions.

| Source | Grades | Evidence of use | Cohort or exposure | Selection evidence |
|---|---|---|---|---|
| NYSED 2022 released Math | 4, 5, 6 | Six Math PDFs delivered as three student/key pairs on November 19, 2026 | Cohort and administration date unrecorded | [Exact papers, hashes and question IDs](ny2022/data/sources.json) |
| NYSED 2022 released ELA | 4, 5, 6 | Six ELA PDFs delivered as three student/key pairs on November 19, 2026 | Cohort and administration date unrecorded | [Exact papers, hashes and question IDs](ny2022/data/sources.json) |
| NYSED 2024 released Math | 4, 5, 6 | October 3, 2026 mock packets prepared | Classroom use unverified | [Golden reference inventory](golden-reference-inventory.md) |
| NYSED 2025 released Math | 4, 5 | One- and two-column packets prepared in May 2026 | Classroom use and exact item overlap unverified | Confirm with teacher before selecting |
| NYSED 2025 released ELA | 6 | Used in the historical benchmark regeneration | Classroom use unverified | [Historical source inventory](golden-assets.json) |
| North Carolina 2025–26 EOG Math released forms | 4, 5, 6 | User reported the proposed papers are already used in class | Cohort and assigned item IDs unrecorded | Exclude for that class unless teacher confirms a fresh selection |

## Before selection

1. Identify the intended class with a stable class or cohort label. Look up candidate papers by testing program, year, subject, grade and source SHA-256. Record the intended cohort in the run record.
2. Compare the candidate question IDs and, for ELA, passage identities with prior selections. A different file name or PDF hash can still represent the same paper. Treat the passage itself as exposure even when the next question selection differs.
3. Exclude confirmed repeated content for the same cohort. When the cohort or item-level exposure is unknown, flag it for the source approval checkpoint and ask the teacher to confirm before reuse. Keep delivered, administered and internal-only records distinct.
4. Record what actually happened after delivery or classroom use. Add a dated row or update an existing row with source identity, exact used question IDs or passages, cohort label, status and evidence. Record cohort labels without student names.

The table is seeded from the evidence available for this run. Add earlier administrations as their source and cohort records are recovered.
