# Generate weekly practice worksheets

**Status:** Proposed target process, derived from the November 16 Math and ELA retrospective. This is a shared specification, not a claim that every component is deployed.

![End-to-end swimlane diagram](./end-to-end-swimlane.svg)

[Open scalable diagram](./end-to-end-swimlane.svg)

## Purpose and scope

Produce curriculum-aligned Math and ELA student worksheets and teacher keys, independently verify content, obtain human approval, publish the latest approved weekly set, and retain evidence for future improvements. See [Math specifications](../generate_math_worksheets/) and [ELA specifications](../generate_ela_worksheets/) for domain details. This shared specification does not replace them.

## Responsibility model

| Lane | Responsibilities |
|---|---|
| Human | Weekly intent, educational judgment, approval of RunSpec and final release, explicit exceptions |
| AI / LLM | Source selection, question design, reasoning, independent semantic review, repairs and retrospective |
| Harness | Context assembly, sequencing, tool invocation, gate enforcement, retries and execution state |
| Code / tools | Deterministic configuration checks, mathematical recomputation, schema and PDF validation, rendering and publishing |
| Storage / knowledge | Curriculum, configurations, source history, templates, versioned artifacts, evidence and operational history |
| External automation | Existing Windows print function reads the shared PrintReady folder independently |

Human decides; AI reasons; harness coordinates; code executes and verifies; storage remembers.

## End-to-end lifecycle

| Phase | Sequence | Outputs |
|---|---|---|
| 01 PreRun | Initialize run; refresh curriculum, configurations, history; resolve weekly scope; select ELA sources and Math topics; preflight; estimate runtime; assemble RunSpec; obtain G1 approval | Approved RunSpec PDF + JSON |
| 02 Run | Dispatch approved Math/ELA scope; design structured content bank; independently solve or review; run objective checks; repair and reverify; render; inspect final exports | Student and teacher PDFs, content and export QA evidence |
| 03 PostRun | Aggregate QA; disclose exceptions; obtain G2 approval; verify exact approved artifacts; publish combined weekly batch; verify readback; reconcile logs; retrospective | QA report, evidence, release manifest, RunLog, improvement register, PrintReady copies |

G1 and G2 are the two primary human approval boundaries. Math's existing additional question-design and pedagogical checkpoints remain in force until explicitly consolidated. A rejected RunSpec returns to planning; a rejected release returns to the affected content or rendering stage, followed by re-verification and renewed approval. Blocking failures stop progression. A material RunSpec change requires renewed G1 approval; changed release artifacts require renewed G2 approval.

## Verification and correction

- Separate generation from review: Math independently recomputes answers; ELA independently predicts answers before seeing the proposed key and checks supporting text, ambiguity, distractors and source fidelity.
- Code checks exact counts, schemas, allocation, mathematical constraints, text/key parity, page size, pagination and fingerprints. AI editorial or visual judgment is not mislabeled as deterministic proof or human sign-off.
- Aggregate all applicable registry rules, distinguishing PASS, FAIL, NOT_VERIFIED and not applicable; record the method and evidence. Do not equate tests passing with complete educational certification.
- Repair affected content, rerun relevant checks and regressions, and escalate persistent failures. Explicit authorized exceptions remain NOT_VERIFIED, not PASS.

## Storage and release contract

Keep the phase-first weekly folder architecture separately for Math and ELA:

    outputs/
      01-PreRun/YYYY-MM-DD/   RunSpec PDF + JSON, preflight
      02-Run/YYYY-MM-DD/      Student and teacher PDFs only
      03-PostRun/YYYY-MM-DD/  QA, evidence, logs, manifests, improvements

The date is the instructional Monday. Working content banks and source evidence belong in designated working/evidence locations, not the worksheet-only Run folder.

Shared PrintReady is the configured flat delivery location, not the historical system of record. Validate both in-scope approved subject sets before cleaning previous-week print copies; preserve dated originals. A same-week correction preserves the other subject's current files. Serialize publishers; verify names, counts, sizes, IDs and hashes when available. Recover the prior verified set if publication fails. No report or log belongs in PrintReady.

The existing Windows printing function is independent and unchanged. No pause/resume handshake is required. Drive replacement is not atomic; schedule publication to finish before printing.

## Observability and continuous improvement

Capture run ID, phase, step, estimated duration, measured active elapsed time, human wait time, retries, status, input/output references and evidence from initialization onward. Emit Markdown and JSON RunLogs and reconcile their final state with the release manifest before closing. Missing measurements are unknown rather than zero.

Inner loop: generate → verify → evaluate → repair → reverify. Outer loop: retrospective → defect/root cause → policy, code, prompt or test improvement → regression validation → next RunSpec. Preserve historical evidence and durable issue IDs.

## Normal human interaction target

1. Initiate the week's run.
2. Approve the resolved RunSpec.
3. Approve the verified release with any explicitly authorized exceptions.

Additional human intervention occurs for domain-required checkpoints, material changes or unresolved educational risks. Full end-to-end automation, independent ELA editorial coverage and live runtime instrumentation remain hardening work.

## Diagram conventions

Columns represent responsible actors; bands represent lifecycle phases. Solid arrows show progression or artifact handoff; dashed amber arrows show content repair. The two human approval nodes also permit rejection and rework as described above. The external print function lies outside the Factory boundary. SVG uses editable vector text and does not depend on an AI model or diagram rendering service.
