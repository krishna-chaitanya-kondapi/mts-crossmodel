# Resume Mock Assessment implementation

Read this file, AGENTS.md, constitution.md, specs/generate_mock_assessment/definition-of-done.md, acceptance-criteria.json, implementation-checkpoint.json, and docs/software-factory/verification-driven-execution.md.

The current state is NOT_DONE at iteration 21. All 76 mandatory criteria remain NOT_VERIFIED in the acceptance registry report. Code and draft artifacts exist, but criterion-level revision-bound verification is unfinished. Development is authorized. Production publication requires human approval.

## Local setup

Use Python 3.11 or newer. From the repository root:

    python -m pip install -r requirements.txt -r specs/generate_mock_assessment/resume/requirements.txt
    python -m pytest tests -q
    python scripts/resume_mock_assessment.py --prepare
    python scripts/resume_mock_assessment.py --render

The test suite writes tracked Weekly Practice transaction fixtures. Run in an isolated checkout or record the initial changes before restoring test-generated files. The last full test run passed 248 tests at iteration 10. Later renderer changes need fresh tests.

## Current implementation

The dedicated scripts/generate_mock_assessment.py CLI supports grade4-student, grade5-student, teacher-key, and ela-teacher. Math student profiles validate fixed NYSED source hashes and exact question selections. Teacher profiles use structured manifests. Weekly generation is independent.

The Grade 5 draft has three student pages and one teacher page, matching the delivered golden page counts. All nine constructed-response solutions were compared to official exemplars. Grade 4 has four student pages and one teacher page. Q26 is full width. Grade 4 Q36 accepts 68–78 degrees and Q38 accepts right or isosceles triangles.

ELA has a four-page student trial outside the CLI and a two-page teacher CLI. The teacher key reuses historical YPQA content. It needs typography, readability, independent academic verification, and rubric checks. Student passage text currently comes from the historical delivered transcript, including two image-only official source pages. Compare it to the official source before claiming source fidelity.

## Exact next actions

1. Repair ELA teacher punctuation and readable two-page typography. Verify all 14 answers with passage evidence, distractor review and official CR scoring guidance.
2. Validate ELA paragraphs and headings against source pages 9–11 and 15–17, especially image-only pages 10 and 16. Question pages are 12–14 and 18–21. Original Q8–14 become output Q1–7. Q22–28 become Q8–14.
3. Promote the ELA student trial into the product CLI with canonical source-based manifests. Remove its runtime dependency on the golden PDF after validating the transcription.
4. Complete Grade 4 academic and fidelity review and repair inefficient fourth-page use. Preserve all 28 items and full-width Q26. Recheck all pages and clearances.
5. Address RunSpec validation/PDF, configuration, repeatability, approval gates, coordinated release requirements, runtime capture, repair tests and remaining registry criteria.
6. Run all paired historical regressions and full Weekly Practice tests. Bind PASS records to the final revision, registry hash and exact evidence hashes. Missing evidence remains NOT_VERIFIED.

## Files and evidence

resume/inputs/golden contains recovered NYSED sources, official Math scoring materials and delivered historical references. Grade 4 references are staged review outputs. Grade 5 and ELA were delivered without explicit final acceptance in the recovered chats. The ELA Drive files' byte identity with the named ChatGPT Library outputs is unverified.

resume/inputs contains renderer manifests. resume/evidence contains reports, tests, hashes, comparisons, checkpoint snapshots and review PDFs. resume/scripts contains prior extraction and diagnostic scripts. These scripts originally ran from the parent workspace and use work/ and outputs/. The resume launcher reconstructs that layout locally.

## Checkpoint convention

At each logical checkpoint update implementation-checkpoint.json, the Markdown and JSON verification reports, defect records, exact next actions, and the dashboard. Regenerate the portable bundle with scripts/package_mock_resume.ps1. Commit all required code and state together locally. Include source fingerprints and distinguish last-tested revision from current working changes. Never mark criteria PASS solely from a page count, artifact hash, or a historical assistant's QA claim.

Keep this file current so another agent can resume without chat history.

## Repository takeover at each checkpoint

Run from the repository root:

    python scripts/checkpoint_mock_assessment.py
    python scripts/checkpoint_mock_assessment.py --verify

Commit the code, canonical checkpoint, reports and resume directory together, then push the development branch. Record actual test results and unresolved defects before the checkpoint refresh. Hash verification checks file identity. It does not establish academic correctness.

The next agent can clone this branch, read this guide, install the two documented requirements files, run the preparation command and regenerate the integrated PDFs. The ELA student trial remains available under resume/scripts/ela_student_trial.py, with its provenance caveats above. The bundle can be regenerated as a secondary delivery option.
