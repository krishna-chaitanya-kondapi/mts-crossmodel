# Weekly Math Worksheet Requirements

## Purpose

Define the functional and non-functional requirements for a deterministic, human-supervised MTS worksheet system. This document is the requirements input for the system design and is organized by functional area.

## Functional Areas

| ID | Functional Area | Responsibility |
|---|---|---|
| FA-01 | Setup Subject and Standards | Establish reusable subject context and authoritative curriculum knowledge. |
| FA-02 | Configure Worksheet System | Define worksheet types and configuration-driven behavior. |
| FA-03 | Prep Cycle | Prepare a weekly or special cycle and resolve its curriculum scope. |
| FA-04 | Generate Worksheet | Create and verify grade-level worksheet content and answer keys. |
| FA-05 | Format Worksheet | Format, quality-check, and place verified grade-level worksheet artifacts. |

## Functional Requirements

| ID | Functional Area | Requirement | Acceptance Criteria |
|---|---|---|---|
| FR-01 | FA-01 | The system shall maintain subjects and their reusable instructional context. | A subject such as Math can be selected for a cycle and links to its curriculum knowledge. |
| FR-02 | FA-01 | The system shall maintain versioned Cabarrus County Schools pacing and NC standards data by subject, grade/course, and school year. | Each curriculum record includes source, source URL or identifier, revision or verification date, and confidence. |
| FR-03 | FA-01 | The system shall preserve the distinction between official, strongly inferred, and inferred curriculum pacing. | Inferred pacing is never represented as official or confirmed CCS pacing. |
| FR-04 | FA-02 | The system shall define worksheet types that control shared worksheet behavior. | The current `class` type resolves duration, enabled grades, content mix, verification, gate, formatting, template, and publishing policies. |
| FR-05 | FA-02 | The system shall read `config/mts-math-worksheet-config.yaml` as the runtime-default configuration source. | Runtime configuration applies the precedence: current user instruction, configuration file, then design default. |
| FR-06 | FA-02 | The system shall keep weekly inputs, run state, and one-time overrides outside the global configuration file. | A weekly curriculum selection or special override does not modify configuration defaults unless persistence is explicitly requested. |
| FR-07 | FA-03 | The system shall dynamically determine the current instructional week in the configured `America/New_York` timezone. | A weekly cycle records its resolved week start/end and the calendar basis used. |
| FR-08 | FA-03 | The system shall dynamically resolve this week's curriculum for each selected grade/course from Cabarrus County Schools sources first. | The resolver uses the configured source-priority order only when CCS evidence is unavailable or insufficient and records the resulting confidence and provenance. |
| FR-09 | FA-03 | The system shall create Weekly and Special cycles from one subject, selected grades, current-week curriculum, and approved special overrides. | A cycle records its type, date range, grade scopes, curriculum resolutions, and override revisions. |
| FR-10 | FA-03 | The system shall stop for Gate 1 before question generation. | Gate 1 shows topic, standards, spiral review, count, difficulty, confidence, and source/basis for each selected grade/course. |
| FR-11 | FA-04 | The system shall create one parent Worksheet per Cycle and worksheet type, with one GradeWorksheet for each selected Grade. | A GradeWorksheet can be corrected, verified, formatted, retried, or published without invalidating other grades in the parent Worksheet. |
| FR-12 | FA-04 | The system shall create a versioned Worksheet Spec as the source of truth for every GradeWorksheet. | The same Worksheet Spec revision supplies student questions, answer-key entries, standards mapping, numbering, difficulty, and QA expectations. |
| FR-13 | FA-04 | The system shall stop for Gate 2 before verification and independently verify every approved question before rendering. | Verification failures or ambiguity block rendering until the affected GradeWorksheet is corrected and reverified. |
| FR-14 | FA-05 | The system shall maintain a versioned TemplateManifest for every template policy used to format a GradeWorksheet. | The manifest records template revision, placement slots, style rules, and render invariants; a template revision change requires manifest revalidation. |
| FR-15 | FA-05 | The system shall render a verified GradeWorksheet and its separate answer key using the configured template policy. | Rendering preserves grade counts, Grade 9/10 split, readable math notation, editable Google Docs, and template layout. |
| FR-16 | FA-05 | The system shall perform formatting QA and stop for Gate 4 before final naming or placement. | QA records question and answer counts, numbering, layout, whitespace, wrapping, notation, unresolved placeholders, and key integrity. |
| FR-17 | FA-05 | The system shall stop for Gate 5 before publishing a formatted worksheet/key pair. | No final worksheet/key pair is placed in the configured publishing target without an explicit Gate 5 approval. |
| FR-18 | FA-03, FA-04, FA-05 | The system shall persist run state, gate decisions, revisions, artifacts, and telemetry. | An interrupted run resumes from its last valid state without repeating completed or approved work. |

## Non-Functional Requirements

| ID | Requirement | Acceptance Criteria |
|---|---|---|
| NFR-01 | Deterministic workflow control | Code validates state transitions, gate eligibility, schemas, and output naming; conversational state alone cannot authorize workflow progress. |
| NFR-02 | Human approval integrity | Each protected transition requires a persisted approval decision for the applicable artifact revision. |
| NFR-03 | Correctness | Verification failures block rendering, and answer keys derive from the same Worksheet Spec revision as student worksheets. |
| NFR-04 | Curriculum evidence integrity | Curriculum resolutions retain their school year, source, freshness state, confidence, and supporting evidence. |
| NFR-05 | Recoverability | A run can retry rendering or publication without regenerating approved questions or discarding verified results. |
| NFR-06 | Auditability | Every GradeWorksheet traces to its subject, grade, cycle, parent Worksheet, curriculum resolution, approvals, spec revision, verification, rendered artifacts, and publish outcome. |
| NFR-07 | Template fidelity | Template revisions, rendering invariants, and visual QA results are recorded before publication. |
| NFR-08 | Security and data minimization | Credentials are external to subject, cycle, worksheet, and run records; persisted records contain only necessary operational data. |
| NFR-09 | Observability | Runs capture timestamps, elapsed time, retries, tool calls, cache behavior, and validation failures. |
| NFR-10 | Maintainability | Markdown documents provide requirements and design evidence; runtime control resides in tested code and versioned structured data. |

## Entity Model

| Entity | Functional Area | Purpose |
|---|---|---|
| Subject | FA-01 | Reusable academic domain, such as Math. |
| Grade | FA-01 | Reusable instructional grade or course within a Subject, such as Grade 6 or Grades 9 & 10 Combined. |
| CurriculumSource | FA-01 | Authority, freshness, and revision information for a curriculum source. |
| CurriculumMapping | FA-01 | Grade/course and school-year curriculum knowledge with provenance and confidence. |
| WorksheetType | FA-02 | Shared worksheet behavior, such as the current `class` type. |
| GradeBlueprint | FA-02 | Grade/course defaults for question count, content mix, and structure. |
| TemplateManifest | FA-05 | Template revision, placement slots, style rules, and rendering invariants. |
| Cycle | FA-03 | Weekly or Special planning period for one subject. |
| GradeScope | FA-03 | Cycle-specific selection of a Grade. |
| CurriculumResolution | FA-03 | Current-week curriculum selected for a grade scope. |
| CycleOverride | FA-03 | Approved temporary cycle-specific change. |
| Worksheet | FA-04 | Parent definition shared by all grade artifacts for a Cycle and worksheet type. |
| GradeWorksheet | FA-04 | Independently controlled artifact for one Grade. |
| WorksheetSpec | FA-04 | Versioned structured source for a GradeWorksheet. |
| Question | FA-04 | A question and its instructional/verification metadata. |
| VerificationResult | FA-04 | Per-question and aggregate validation evidence. |
| GateDecision | FA-03, FA-04, FA-05 | Persisted user decision for a protected workflow transition. |
| RenderArtifact | FA-05 | Rendered GradeWorksheet/key artifact and formatting QA result. |
| PublishRecord | FA-05 | GradeWorksheet publication target, paired-artifact outcome, and timestamps. |
| Run | FA-03, FA-04, FA-05 | Execution state, checkpoints, telemetry, and recovery context. |

## Workflow Invariants

1. The current-week curriculum resolution occurs before Gate 1 and question generation.
2. Gate 1 through Gate 5 remain separate, explicit approvals.
3. One Worksheet contains one GradeWorksheet per selected Grade.
4. Each GradeWorksheet has independent specifications, verification, formatting, retry, and publication evidence.
5. A Grades 9 & 10 combined GradeWorksheet has 16 Grade 9 questions followed by 16 Grade 10 questions unless a current-run override is approved.
6. Publication occurs only after final QA and explicit Gate 5 approval.

## Design Traceability

The system design at `specs/01.generate-weekly-math-worksheets/design.md` shall reference the requirement IDs in this document. Each requirement must trace to the applicable functional area, architecture component, entity, implementation slice, and verification evidence.