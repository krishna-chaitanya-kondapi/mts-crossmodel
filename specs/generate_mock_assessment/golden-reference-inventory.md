# Golden run inventory

## User-designated golden runs

On November 19, 2026, the user designated three past ChatGPT runs as golden references: two conversations linked from Mock Assessment history search, and one conversation in the MTS Math AI Generation project. The private conversation links remain in the request, not in this repository.

Authenticated review resolved all three handoffs. The counts and selections below were cross-checked against the [historical NYSED item maps](../../outputs/historical-source-item-maps.json). Page counts and layout details are comparison targets, not acceptance results.

| Conversation | Source and checked selection | Final files named in chat | PDF identity |
|---|---|---|---|
| Format Math Mock Test (first link) | NYSED Grade 5 Math 2024, 28 items (19 MC, 9 CR) | `MTS-NY-Math-Grade5-2024-Worksheet.pdf` and `MTS-NY-Math-Grade5-2024-Answer-Key.pdf` | Filenames and reported page counts match the [prior Drive comparison](../../outputs/grade5-golden-comparison.json); chat attachment bytes not re-fingerprinted. |
| Format ELA Mock Test (second link) | NYSED Grade 6 ELA 2025, Q8–14 and Q22–28 (12 MC, two 2-credit CR) | `MTS-ELA-MockTest-6thGrade-2026-09-23.pdf` and `MTS-ELA-MockTest-6thGrade-2026-09-23-KEY.pdf` | Both authenticated library downloads matched the existing local goldens and the [historical fingerprint inventory](../../outputs/historical-pdf-sha256.json) byte-for-byte by SHA-256. The prior Drive filenames say `WeeklyWorksheet`, but the hashes match the mock-test library files. This is an artifact alias, not a Weekly Practice dependency. |
| Create Mock Test (project link) | NYSED Grade 4 Math 2024, 28 listed items (19 MC, 9 CR) | `MTS-NY-Math-Grade4-2024-Worksheet-REVIEW.pdf` and `MTS-NY-Math-Grade4-2024-Answer-Key-REVIEW.pdf` | Filenames match the [historical fingerprint inventory](../../outputs/historical-pdf-sha256.json) and reported page counts match the recovered review pair; chat attachment bytes not re-fingerprinted. The handoff headline says 29 items (10 CR), but its enumerated selection and the NYSED map both give 28 (9 CR). Use the checked selection. |

- **Grade 5 Math:** 3 student pages and 1 key page; questions atomic, two columns; Q43 diagram at 70%, four other original diagrams at 75%. The handoff reports Q40 corrected to 35 tiles and 8¾ square feet. It names a generator, run manifest and layout metrics, but did not expose a final RunSpec or durable copies of those files.
- **Grade 6 ELA:** 4 student pages and 2 YPQA key pages. *Cracking Code Purple* and *Excerpt from New York: Local Legacies* are the two selected passages. The cipher-machine figure is on page 2; the final two questions are full width with five response lines each. The 12 MC answers agree with the recorded official map. Later audit findings for excess whitespace on pages 1 and 3 were not applied to the delivered files. The handoff identifies a transient script; its later production manifest is not the original run manifest.
- **Grade 4 Math:** 4 student pages and 1 review key page, two columns except full-width Q26, with figure scales reported at 70–75%. The handoff records final corrections for crop completeness at Q26 and Q34 and fuller source prompts at Q41 and Q43. It identifies a transient script but no final RunSpec or manifest. The Grade 4 **2025** worksheet mentioned in this chat is a layout input, not the designated Grade 4 **2024** output.

The handoffs establish reported delivery (Grade 4 staged for review), not independent QA, explicit final acceptance, permission to reuse the NYSED material, or approval to publish. Do not freeze authentic historical RunSpecs from these summaries alone: recover the Math attachment bytes and any available generation records, and label any reconstructed specifications as such.

## Previously recovered artifact candidates

Drive metadata discovered; final approval, bytes and content not yet independently verified.

| Candidate | Drive ID |
|---|---|
| NY Math 2024 grade 6 source | 1qGaUQ6mwNGRbhyp1z5reEbQkk7oQGnkP |
| Grade 6 worksheet | 1t6TZ_JT9KvS_rDK-tW9h-oQTysduON7E |
| Grade 6 key | 16zNHqCkvqtDQrGD5l3-0CSbEWhA_OCOT |
| NY Math 2024 grade 5 source | 12HV38VavNpVfIJfndIkzXtZVzHpV_4Uf |
| Grade 5 worksheet | 1Mn5GgTnisapYDyz66fb4b0BCoolgsvmo |
| Grade 5 key | 1U_-pD3OgU7VHkwr4EMbACnG4JAca9LX9 |
| NY ELA 2025 grade 6 source | 1f7Ar_K3aRrvJLpreFS9dZfVgWsZp5i97 |
| NY ELA 2024 grade 6 source | 1Vf486qZ1cuAQsqTRcivnP_mjyD6uIShE |

The Grade 6 Math pair remains outside the three designated references. The 2024 ELA source is not the selected ELA edition.
