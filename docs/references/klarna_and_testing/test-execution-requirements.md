# Functional Testing Platform — Product Management
## Test Execution — User Stories and Acceptance Criteria

> **Layer:** Product Management — reusable test product (portable across projects)
> **Product:** Functional Testing as a Product (Sterling OMS domain, portable to other projects)
> **Focus of this document:** **Test Execution** value stream — the first delivery slice
> **Structure reference:** [DMI-551 requirements.md](../../DMI-551-dom-klarna-bnpl/01-intent/requirements.md)
> **Status:** Draft — Test Execution prioritised first

This document captures the INVEST-compliant user stories and Gherkin acceptance criteria for the **Test Execution** area of the Functional Testing product. It defines precisely what is required to run `/execute-test` — the inputs, preconditions, setup, reusable test blocks, and outputs — so that the capability can be lifted into any project by configuration only.

---

## Table of Contents

- [1. Epic](#1-epic)
  - [1.1 Guiding Scope Map (Full Scope)](#11-guiding-scope-map-full-scope)
- [2. Key — Glossary of Terms](#2-key--glossary-of-terms)
- [3. Story Review Table](#3-story-review-table)
- [4. Execution Prerequisites — What `/execute-test` Requires](#4-execution-prerequisites--what-execute-test-requires)
- [5. User Stories](#5-user-stories)
  - [TE-1 Local Machine Setup](#te-1--local-machine-setup)
  - [TE-2 Test Environment Setup](#te-2--test-environment-setup)
  - [TE-3 Reusable Test Blocks (Multi-System)](#te-3--reusable-test-blocks-multi-system)
  - [TE-4 Test Workflow Composition](#te-4--test-workflow-composition)
  - [TE-5 Test-Script-Driven Execution](#te-5--test-script-driven-execution)
  - [TE-6 Execution Result Capture & Zephyr Sync](#te-6--execution-result-capture--zephyr-sync)
  - [TE-7 Environment-Agnostic Configuration](#te-7--environment-agnostic-configuration)
- [6. Story Traceability](#6-story-traceability)
- [7. Open Items Affecting Delivery](#7-open-items-affecting-delivery)
- [8. Non-Functional Criteria (testable)](#8-non-functional-criteria-testable)
- [9. Future Enhancements](#9-future-enhancements)

---

## 1. Epic

**Epic:** Deliver **Test Execution** as the first slice of the Functional Testing product — a test-script-driven, environment-agnostic capability that executes a functional test case against any target environment and records the result, reusing encoded multi-system test blocks.

**Product outcome:** A QA engineer on any project can run `/execute-test`, and the framework will provision test data, environment access, mTLS certificates, and user credentials (for OrderHub, Call Centre, and Store), execute the case through reusable test blocks spanning the integrated system landscape (Hybris, OMS, Payment systems, Databases, APIs, ESB/SAP, CARS), compare against expected results, and sync the outcome to Zephyr — with no code changes required to move between projects, including coverage across both US and UK brands, order types, and fulfillment types.

**Scope boundary:** This slice covers the **build → compose → execute → report** chain for functional test execution — developing reusable test blocks (TE-3), composing them into workflows (TE-4), executing against a target environment (TE-5), and capturing results (TE-6), plus the local/environment setup and portability that enable it. Upstream test planning, strategy, and high-level test-case generation, and downstream defect triage and retest/closure, are separate slices (tracked in the parent product backlog). The system-under-test (e.g. Klarna BNPL) is the *consumer*, not the product.

**Portability principle:** Every execution asset (test script, data seed, test block, config) must be parameterised and environment-agnostic. Moving to a new project is a configuration change, not a code change.

### 1.1 Guiding Scope Map (Full Scope)

> This section is the guiding map for scope and structure; detailed story content follows in later sections.

```text
L0. Product
`-- Functional Testing as a Product
  `-- L1. Full Scope Hierarchy
    |-- L2.1 Area: Test planning
    |   |-- L3 Capabilities: Test Data Setup, Runbook and Execution Implementation, Application Setup, Certification/Authorisation setup
    |   |-- L3 Most Important Capabilities: Test Plan Template (Scope, Timeline)
    |   |-- L3 Slash Commands: /create-test-plan
    |   `-- L3 User Stories
    |       `-- L4 User Story Label: TBD
    |           `-- L4 One-liner ACs: TBD
    |
    |-- L2.2 Area: Test strategy
    |   |-- L3 Capabilities: Framework Architecture, Tool Selection and Design, Scope Requirement Traceability/Validation
    |   |-- L3 Most Important Capabilities: Design Template, Domain Knowledge, Tool Guidance/Standards
    |   |-- L3 Slash Commands: /create-test-strategy
    |   `-- L3 User Stories
    |       `-- L4 User Story Label: TBD
    |           `-- L4 One-liner ACs: TBD
    |
    |-- L2.3 Area: Test generation
    |   |-- L3 Capabilities: Parameter/Flow/Batches, JIRA/Zephyr Integration
    |   |-- L3 Most Important Capabilities: Test Case Template (Test cases and scripts)
    |   |-- L3 Slash Commands: /create-testcases-design, /create-testcases
    |   `-- L3 User Stories
    |       |-- L4 User Story Label: TG-1 Requirement Intake (JIRA / TDD)
    |       |   `-- L4 One-liner ACs: Requirements are ingested with stable IDs; gaps are flagged, never invented.
    |       |-- L4 User Story Label: TG-2 Parameter-Driven Generation (compound: TG-2.1 Parameter Catalog, TG-2.2 Permutation)
    |       |   `-- L4 One-liner ACs: A shared parameter catalog is expanded into valid permutations; out-of-scope ones are documented as exclusions.
    |       |-- L4 User Story Label: TG-3 Test Flow Generation
    |       |   `-- L4 One-liner ACs: Each end-to-end test flow (and branch) becomes a case referencing reusable blocks.
    |       |-- L4 User Story Label: TG-4 Suite & Batch Assembly
    |       |   `-- L4 One-liner ACs: A prioritised, de-duplicated suite is batched by any parameter across the required test types.
    |       |-- L4 User Story Label: TG-5 Test Case Template
    |       |   `-- L4 One-liner ACs: Each case renders to a review-ready document with stable steps, required fields, and traceability.
    |       |-- L4 User Story Label: TG-6 Test Script Design
    |       |   `-- L4 One-liner ACs: Case steps are mapped to reusable blocks/workflows and a matching script skeleton is produced with explicit gaps.
    |       |-- L4 User Story Label: TG-7 Test Case Status & Lead Approval
    |       |   `-- L4 One-liner ACs: Cases move Not Started -> WIP -> Ready and require lead approval before execution.
    |       |-- L4 User Story Label: TG-8 JIRA / Zephyr Integration
    |       |   `-- L4 One-liner ACs: Eligible cases are pushed to Zephyr idempotently and linked to their JIRA stories.
    |       `-- L4 User Story Label: TG-9 Coverage & Traceability
    |           `-- L4 One-liner ACs: A coverage matrix flags uncovered requirements, orphan cases, and preserves many-to-many mappings.
    |
    |-- L2.4 Area: Test execution
    |   |-- L3 Capabilities: Test Data Setup, Runbook and Execution Implementation, Application Setup, Certification/Authorisation setup
    |   |-- L3 Most Important Capabilities: Creation/Updation of Testcase, Test Execution Scripts
    |   |-- L3 Slash Commands: /execute-test-case
    |   `-- L3 User Stories
    |       |-- L4 User Story Label: TE-1 Local Machine Setup
    |       |   `-- L4 One-liner ACs: Local setup is complete, repeatable, and blocks execution if prerequisites are missing.
    |       |-- L4 User Story Label: TE-2 Test Environment Setup
    |       |   `-- L4 One-liner ACs: Environment, data, and credentials are provisioned and validated before execution.
    |       |-- L4 User Story Label: TE-3 Reusable Test Blocks (Multi-System)
    |       |   `-- L4 One-liner ACs: Reusable blocks define strict I/O contracts, waits, and idempotency.
    |       |-- L4 User Story Label: TE-4 Test Workflow Composition
    |       |   `-- L4 One-liner ACs: Workflows compose blocks in order with declared gates and alternate branches.
    |       |-- L4 User Story Label: TE-5 Test-Script-Driven Execution
    |       |   `-- L4 One-liner ACs: Runtime enforces sequence/retries/timeouts and produces deterministic verdicts.
    |       |-- L4 User Story Label: TE-6 Execution Result Capture and Zephyr Sync
    |       |   `-- L4 One-liner ACs: Evidence and logs are persisted and Zephyr/JIRA sync remains recoverable.
    |       `-- L4 User Story Label: TE-7 Environment-Agnostic Configuration
    |           `-- L4 One-liner ACs: Portability is configuration-only with pre-run config validation.
    |
    |-- L2.5 Area: Bug Tracking and Reporting
    |   |-- L3 Capabilities: JIRA/Zephyr Integration
    |   |-- L3 Most Important Capabilities: Tracking template
    |   |-- L3 Slash Commands: /create-defect
    |   `-- L3 User Stories
    |       `-- L4 User Story Label: TE-6 Execution Result Capture and Zephyr Sync
    |           `-- L4 One-liner ACs: Results and evidence are recorded with re-sync support when Zephyr is unavailable.
    |
    `-- L2.6 Area: Bug Retesting and Closure
      |-- L3 Capabilities: TBD
      |-- L3 Most Important Capabilities: TBD
      |-- L3 Slash Commands: TBD
      `-- L3 User Stories
          `-- L4 User Story Label: TBD
              `-- L4 One-liner ACs: TBD
```

---

## 2. Key — Glossary of Terms

> Plain-language definitions of the technical terms used in this document, so it is readable by product, QA, and engineering alike.

**Execution & lifecycle terms**

| Term | Meaning |
|---|---|
| Test cycle run | A scheduled execution of a set of test cases (in Zephyr) against a target environment for a given release/sprint |
| Verdict | The outcome of a test case: **Passed**, **Failed**, or **Blocked** |
| Orchestration | Composing and running reusable blocks in the sequence defined by the test script |
| Expected results | The defined expected values/state used to decide whether a step Passed or Failed |
| Regression testing | Re-running existing test cases to confirm previously working behaviour still works after a change |

**Asset & artefact terms**

| Term | Meaning |
|---|---|
| Test case asset | The generated, parameterised definition of a test (steps, data references, expected results) |
| Test script (`.ts`) | The executable Playwright/TypeScript file that runs a test case; it encodes the test workflow (block order) |
| Test workflow | The ordered flow of test blocks that make up an end-to-end scenario. Composed in TE-4, executed in TE-5 |
| Test block | A reusable, parameterised action defined as **Application + Functionality + Invocation method** (e.g. *OMS · Order Creation · REST `createOrder`*). Built in TE-3, composed into a workflow in TE-4, executed in TE-5 |
| Run log (per-run Markdown in `_run-logs/`) | A per-run Markdown log at `_run-logs/{TC-ID}/{TC-ID}_{yyyyMMdd}_{HHmm}_{RESULT}.md` (plus a rolling `index.md`) capturing summary, phase timings, assertions, and retry log — used for telemetry, uploading results to Zephyr, and logging JIRA defects |
| Evidence store | Where logs, responses, and screenshots are persisted for audit |
| Result sink | The destination that records Pass/Fail plus evidence (Zephyr / JIRA) |
| Zephyr | JIRA-integrated test management tool used to plan test cycles and record results |
| Slash command | An agent command (e.g. `/execute-test`) that triggers a capability |

**Systems, channels & security terms**

| Term | Meaning |
|---|---|
| OMS (Sterling) | IBM Sterling Order Management System — the core order platform |
| Hybris | SAP Commerce — the checkout / commerce front end |
| OrderHub | Sterling order management console (UI channel) |
| Call Centre | Agent-facing channel for order and service actions |
| Store | In-store channel / application |
| ESB / SAP | Enterprise Service Bus / SAP — receives outbound reconciliation feeds |
| CARS | SAP CAR settlement / financial reconciliation system |
| mTLS certificate | Mutual-TLS client certificate (e.g. IBM-issued `.p12` → `.pfx`) required to reach OMS securely |
| Basic auth / user setup | Username/password credentials for application channels, resolved from config (never hard-coded) |

**Story Review Table column meanings**

| Column | Meaning |
|---|---|
| Functional Area | The top-level lifecycle area a story belongs to: **Local Setup** · **Environment Setup** · **Test Asset Development** · **Test Execution** |
| Sub Area | The finer grouping within an area: Local Machine Provisioning · Environment & Access Provisioning · Reusable Building Blocks · Workflow Orchestration · Execution Engine · Result Capture & Reporting · Configuration Portability |
| Primary Trigger | The event that starts the story's behaviour |
| Core Behavior | What the story does when triggered |
| Product Outcome | The value delivered to the consumer of the framework |
| INVEST Risk | How well the story meets INVEST (Independent, Negotiable, Valuable, Estimable, Small, Testable) |

**Personas / user roles** — used consistently in the story cards below:

| Persona | Who they are | Stories |
|---|---|---|
| **QA Engineer** | Runs functional & regression tests day-to-day; primary user of `/execute-test` and `/setup-test-env` | TE-2, TE-5 |
| **Automation / Framework Engineer** | Builds and maintains the reusable blocks and workflows | TE-3, TE-4 |
| **QA Lead** | Owns test cycles, reporting, and status visibility to the team | TE-6 |
| **Onboarding Engineer** | A QA/dev setting up a new machine or adopting the framework in a new project | TE-1, TE-7 |

---

## 3. Story Review Table

> One-row-per-story governance overview for the Test Execution slice.

| Story ID | Functional Area | Sub Area | Primary Trigger | Core Behavior | Product Outcome | Slash Command | Reusability Concern | INVEST Risk | Priority | Status |
|---|---|---|---|---|---|---|---|---|---|---|
| TE-1 | Local Setup | Local Machine Provisioning | New engineer / clean machine | One-time install of toolchain, Playwright browsers, Python deps, and generation of local mTLS certificate | A QA engineer can run the suite locally without environment drift | `/setup-test-local` | Setup steps documented and repeatable | Low | P1 | Ready |
| TE-2 | Environment Setup | Environment & Access Provisioning | Test cycle run | Offer a selectable list of target environments, applications (OrderHub, Store, Call Centre, Hybris), brand/enterprise targets (US + UK), order types, fulfillment types, and payment types (CC/Klarna/PayPal, or a custom entry); provision test data, establish mTLS certificate + user access, and support switching between environments | The environment is prepared and ready before a test runs | `/setup-test-env` | Setup engine project-agnostic | Moderate | P1 | Ready |
| TE-3 | Test Asset Development | Reusable Building Blocks | A workflow needs a system action | Build reusable test blocks — each an **Application + Functionality + Invocation method** unit (e.g. *OMS · Order Creation · REST*) encapsulating input params (from config/state), output capture to shared state, and its own waiting / polling / retry strategy | A versioned library of reusable, parameterised blocks any workflow can call across OMS, Hybris, Klarna, DB, ESB/SAP, CARS | `/create-test-block` | The core reusable IP — blocks stay environment-agnostic and parameterised | High (core value) | P1 | Pending OQ-E2 |
| TE-4 | Test Asset Development | Workflow Orchestration | An end-to-end scenario must be assembled from blocks | Orchestrate TE-3 blocks into an ordered, state-passing workflow — sequence phases, hand each block's output to the next block's input, and **declare** the cross-block synchronisation (fixed settle waits, decision gates, long-service timeouts, retry-with-fallback, known-condition branches, hard-fail gates) | A single repeatable end-to-end flow (the test script) ready for execution | `/create-test-workflow` | Workflow is data/config over reusable blocks — reordering must not touch blocks | Moderate | P1 | Pending OQ-E1 |
| TE-5 | Test Execution | Execution Engine | A test case / cycle is invoked | Run the TE-4 workflow sequentially (`workers=1`) against a prepared environment — **enforce** the TE-4-declared synchronisation (waits, decision gates, branches), honour the timeouts, persist per-run state to decide restart-vs-resume on re-invocation, capture phase timings + retry log, compare actual vs expected results, and record the verdict | The workflow runs to a clear, evidenced Pass / Fail / Blocked verdict | `/execute-test` | Execution engine project-agnostic; only config changes per project | High — integration point (TE-2·TE-4·TE-6·TE-7) | P1 | Pending OQ-E1 |
| TE-6 | Test Execution | Result Capture & Reporting | Step/case completes | Write per-run Markdown log to `_run-logs/`; capture result, evidence, timestamp; sync Zephyr; log JIRA defects | Every run produces a traceable result | supports `/execute-test` | Result format tool-agnostic | Low | P2 | Pending OQ-E3 |
| TE-7 | Test Execution | Configuration Portability | New project adoption | Resolve environment/data/creds from external config | Same asset runs in a new project by config only | supports `/execute-test` | Defining product requirement | Medium | P2 | Ready |

**7 stories · 34 acceptance scenarios** — all required to make `/execute-test` work end-to-end.

---

## 4. Execution Prerequisites — What `/execute-test` Requires

> This section makes the dependencies of `/execute-test` explicit. Each item maps to a user story below.

| # | Requirement | Description | Owning Story |
|---|---|---|---|
| R-1 | **Test case asset** | Approved feature test design plus generated `test-cases.json` and `test-suite.xlsx` with steps, test data, expected results, and traceability | TE-5 (consumes output of `/create-testcases`) |
| R-2 | **Test workflow (script)** | The ordered flow of test blocks that make up an end-to-end scenario (the `.ts` test script) | TE-4 |
| R-3 | **Test data** | Seeded orders/customers/items required by the case, tagged for cleanup | TE-2 |
| R-4 | **Environment & application setup** | Target environment reachable; OrderHub, Call Centre, and Store applications available | TE-2 |
| R-5 | **Certificate & user auth** | mTLS client certificate plus basic auth / user credentials, sourced from config, never hard-coded | TE-2 |
| R-6 | **Test blocks** | Reusable multi-system blocks (Hybris, OMS, Payment, Database, API, Call Centre, ESB/SAP, CARS) | TE-3 |
| R-7 | **Environment configuration** | Target environment URLs, credentials, and project identifiers resolved externally | TE-7 |
| R-8 | **Result sink** | Zephyr/JIRA target to record Pass/Fail plus evidence | TE-6 |
| R-9 | **Expected results** | Defined expected values/state to compare actual results against | TE-5 |
| R-10 | **Evidence store** | Location to persist logs, responses, and screenshots for audit | TE-6 |
| R-11 | **Local machine setup** | One-time per-machine toolchain (Node/npm, Playwright browsers), Python bootstrap deps, and generated mTLS `.pfx` | TE-1 |

---

## 5. User Stories

---

### TE-1 — Local Machine Setup

**Status:** Ready
**Functional Area:** Local Setup
**Requirements:** R-11
**Slash Command:** `/setup-test-local` — *precondition, one-time per machine*

```text
As an Onboarding Engineer (a QA/dev joining a project),
I want a documented, repeatable one-time setup for my local machine,
so that I can run the functional test suite locally
without manual guesswork or environment drift between team members.
```

**Local setup capabilities in scope:**

| Capability | Description |
|---|---|
| Toolchain install | Node.js + npm dependencies (`npm install`) and Playwright browsers (`npx playwright install`) |
| Bootstrap runtime | Python and bootstrap-script dependencies used for scenario setup |
| Client certificate | Obtain the issued `.p12` and generate the local mTLS `.pfx` once per machine |
| Local credentials | Resolve user credentials / env vars from local config (never committed) |

> **Examples to try:** a clean machine with no Node/Python; a renewed / expired certificate; a missing `.p12`; wrong or absent credentials.

**Acceptance criteria:**

```gherkin
Scenario: Fresh machine can run the suite after setup
  Given a QA engineer with a clean machine
  When they follow the one-time local setup steps
  Then the toolchain and browser dependencies shall be installed
  And the local mTLS certificate shall be generated once
  And the engineer shall be able to execute a test case successfully

Scenario: Certificate generated once and reused
  Given the local mTLS certificate has already been generated
  When the engineer runs further test cases
  Then the existing certificate shall be reused
  And no regeneration shall be required unless the certificate is renewed

Scenario: Missing local prerequisite is reported clearly
  Given a required tool, dependency, or credential is not present
  When local setup or execution starts
  Then the missing prerequisite shall be named
  And guidance to resolve it shall be provided
  And no test shall run against an incomplete local setup
```

---

### TE-2 — Test Environment Setup

**Status:** Ready
**Slash Command:** `/setup-test-env` — *supports `/execute-test`*
**Requirements:** R-3 · R-4 · R-5
**Depends on:** TE-1

```text
As a QA engineer on any project,
I want to select the target environment and the applications / brand / order / fulfillment / payment dimensions under test, and have that environment prepared —
test data seeded, certificates and user access established — with the ability to switch environments,
so that a test case can execute against a ready, known-good environment of my choosing
without manual preparation, and independently of how the test is run.
```

**Setup capabilities in scope:**

| Capability | Description |
|---|---|
| Target & application selection | Present a selectable list of environments, applications (OrderHub, Store, Call Centre, Hybris) and payment types (CC, Klarna, PayPal…); accept a custom entry; support switching between environments |
| Brand / enterprise selection | Present US and UK brand/enterprise options from configuration (for example: US `0002`,`2000`; UK `3000`,`4000`) |
| Order and fulfillment selection | Present selectable order types and fulfillment types supported by the selected brand/enterprise |
| Test data setup | Provision seeded orders/customers/items required by the case; tag for cleanup |
| Environment setup | Resolve and reach the target environment (Dev/QA/etc.) for each application under test |
| Certificate setup | Establish the mTLS client certificate (e.g. IBM-issued `.p12` → `.pfx`) needed to reach OMS |
| Basic auth / user setup | Provision or resolve user credentials for **OrderHub**, **Call Centre**, and **Store** access channels |

**Selectable targets** — `/setup-test-env` presents these for the user to choose (with a free-text option for anything not listed):

| Category | Options (examples) |
|---|---|
| Target environment | Dev-1 · Dev-2 · QA-1 · QA-2 · UAT-2 · *(or a custom URL / env)* |
| Application / channel | OrderHub · Store · Call Centre · Hybris |
| Brand / enterprise | US: `0002` (Zales) · `0006` · `0008` · `0010` · `5998` · `2000` (Kay) · `2001` (Jared) · `2032` · UK: `3000` (Ernest Jones) · `4000` (H Samuel) |
| Order type | STH · BOPIS · SFS · STS |
| Fulfillment type | SFS · BOPIS · SDD · Curbside · Ship-from-DC |
| Payment type | Credit Card (CC) · Klarna · PayPal · Clearpay · *(or a custom type)* |

> **Examples to try:** a US brand run then a UK brand run; an environment not in the list (custom URL); switching environment mid-cycle; a missing data seed; a certificate not yet generated; two engineers using the same data.

**Acceptance criteria:**

```gherkin
Scenario: User selects the target environment and applications from a list
  Given /setup-test-env is run
  When setup starts
  Then the user shall be presented a list of target environments to choose from
  And a list of applications (OrderHub, Store, Call Centre, Hybris), brand/enterprise options, order types, fulfillment types, and payment types
  And the user shall select the environment and the applications / brand / order / fulfillment / payment dimensions under test

Scenario: User provides a target not present in the list
  Given the list of environments and applications is presented
  When the required target is not in the list
  Then the user shall be able to enter a custom environment or application
  And setup shall proceed against that custom target

Scenario: User selects US and UK brand contexts without changing test assets
  Given a reusable test case and workflow
  When the user runs setup for a US brand/enterprise and later for a UK brand/enterprise
  Then setup shall resolve the correct brand-specific configuration for each run
  And no test source changes shall be required to switch region context

Scenario: Switch the target environment between runs
  Given a case prepared for one environment
  When the user selects a different environment via /setup-test-env
  Then subsequent runs shall target the newly selected environment
  And no test asset shall require modification to switch

Scenario: Provision test data before execution
  Given a test case that requires seeded order/customer/item data
  When the setup phase runs
  Then the required test data shall be provisioned in the target environment
  And the data shall be tagged so it can be cleaned up after the run

Scenario: Certificate and user access established for the target channels
  Given a target environment requiring mTLS and authenticated access
  When the setup phase runs
  Then the mTLS client certificate shall be established for OMS access
  And basic auth / user credentials shall be resolved for OrderHub, Call Centre, and Store
  And all credentials shall be sourced from environment configuration, never hard-coded

Scenario: Setup failure blocks execution with a clear reason
  Given test data, certificate, or user access cannot be established
  When the setup phase runs
  Then execution shall not start
  And the case shall be marked Blocked with the missing prerequisite named
  And no partial or misleading result shall be recorded

Scenario: Tagged test data is cleaned up after the run
  Given test data provisioned and tagged for a run
  When the run completes (Pass, Fail, or Blocked)
  Then the tagged data shall be removed or marked for reclamation
  And it shall not collide with data from other runs or engineers
```

---

### TE-3 — Reusable Test Blocks (Multi-System)

**Status:** Pending OQ-E2
**Requirements:** R-6
**Slash Command:** `/create-test-block` — *core product IP*

> **Purpose:** TE-3 is about **building and maintaining** the block library (the *how* of each action). **Composing** these blocks into a workflow is TE-4; **executing** that workflow is TE-5.

```text
As an Automation / Framework Engineer,
I want to build repeatable actions across every integrated system as reusable, parameterised test blocks,
so that any functional or regression test can be assembled quickly from proven, reusable actions —
cutting test-build time and keeping coverage consistent across releases.
```

**What a test block is** — every block is defined by four things:

- **Application** — the system under test (OMS, Hybris, Klarna/Payment, Database, ESB/SAP, CARS, Call Centre)
- **Functionality** — the business action (order creation, scheduling, release, fulfilment, cancellation, appeasement, refund, verification)
- **Invocation method** — how the action is triggered (REST API, XML-template inject, UI/widget automation, DB query, feed/file check)
- **Block type** — its role: Action · Verification · Waiting · Manual gate

**Block catalog (Application · Functionality · Invocation method · Block type):**

| Block | Application | Functionality | Invocation method | Block type |
|---|---|---|---|---|
| OMS Order Creation API | OMS (Sterling) | Create / inject order | REST `createOrder` + XML template | Action |
| OMS Scheduling API | OMS (Sterling) | `scheduleOrder` | REST API | Action |
| OMS Release API | OMS (Sterling) | `releaseOrder` | REST API | Action |
| OMS Fulfilment API | OMS (Sterling) | Confirm Shipment (ASN) | REST ASN service + XML template | Action |
| OMS Cancellation API | OMS (Sterling) | `cancelOrder` | REST API | Action |
| OMS Appeasement API | OMS (Sterling) | Appeasement via `processOrderPayments` | REST API | Action |
| OMS Refund API | OMS (Sterling) | Return / Refund | REST `createReturnOrder` + `processOrderPayments` | Action |
| Hybris Checkout UI/Page | Hybris | Place order / checkout | UI automation (Playwright) | Action |
| Hybris Order Status UI/Page | Hybris | Retrieve order status | UI / API | Verification |
| Klarna Order Creation Widget/API | Klarna (Payment) | Create BNPL order | Widget automation + REST | Action |
| Klarna Capture/Refund/Cancel API | Klarna (Payment) | Capture · Refund · Cancel authorisation | REST | Action |
| Payment Capture Wait | OMS / Payment | Wait until capture is confirmed | Poll (`processOrderPayments`) | Waiting |
| Database Verification Query | Database | Verify order / payment / status rows | SQL query | Verification |
| ESB/SAP Feed Verification | ESB / SAP | Verify outbound reconciliation feed | Feed / file check (e.g. `yfs_export`) | Verification |
| CARS Reconciliation Check | CARS | Verify settlement / reconciliation record | Query / report check | Verification |
| Manual Approval Gate | Any (manual) | Pause for a human check / approval | Manual / prompt | Manual gate |

> **Block types:** **Action** (performs a business action) · **Verification** (asserts a record or state) · **Waiting** (waits / polls for an async condition) · **Manual gate** (pauses for a human check / approval).

**Delivery breakdown** — TE-3 is a compound story; it is delivered as right-sized per-system sub-stories so each is estimable and small:

| Sub-story | Scope | Blocks |
|---|---|---|
| TE-3.1 | OMS blocks | Order Creation, Scheduling, Release, Fulfilment, Cancellation, Appeasement, Refund |
| TE-3.2 | Hybris blocks | Checkout, Order Status |
| TE-3.3 | Payment blocks | Klarna, Credit Card, PayPal (create / authorize / capture / refund / cancel) |
| TE-3.4 | Verification blocks | Database, ESB/SAP feed, CARS reconciliation |

**Block execution mechanics** — beyond the action itself, every block encapsulates:

| Concern | What the block handles |
|---|---|
| Input | Parameters resolved from config and shared state (e.g. `authorizationId`, `OrderNo`, `OrderHeaderKey`) |
| Invocation | The call itself — REST (mTLS + Basic auth), UI / widget automation, DB query, or feed / file check |
| Output capture | Persists results to shared state for downstream blocks (e.g. `captureId` → `PaymentReference6`) |
| Waiting strategy | Fixed settle wait after async actions; **poll-until-condition** (e.g. call `processOrderPayments` up to 6× at 5s until `PaymentReference6` is populated); long-service timeouts (e.g. up to 180s per shipment call) |
| Retry & fallback | Bounded retries at a fixed interval; parameter fallback (e.g. `ReleaseNo` 1↔2 swap); deadlock retry (e.g. `YFC0100` up to 3×) |
| Known-condition branch | Recognise expected non-errors (e.g. `OMP10079` over-shipment = already shipped) and branch instead of failing |

> **Examples to try:** a block with no async result; a long-running service; a verification block against an empty feed; a duplicate call (idempotency); a manual-gate block.

**Acceptance criteria:**

```gherkin
Scenario: Create a test block with its full definition
  Given a system action to encode (e.g. OMS Order Creation API)
  When the block is created via /create-test-block
  Then the block shall be defined with its Application, Functionality, Invocation method, and Block type
  And its input parameters and output capture (to shared state) shall be declared
  And it shall be added to the reusable block library

Scenario: Set up a block with a declared waiting strategy
  Given a block whose result is produced asynchronously (e.g. a payment capture)
  When the block is created
  Then a waiting / polling strategy shall be declared (interval, bound, and success condition)
  And the strategy shall be part of the block definition, not the workflow

Scenario: Set up a block with composable inputs and outputs
  Given a block being created with declared input parameters
  When its definition is completed
  Then it shall declare the outputs it captures to shared state in a documented shape
  And those declared outputs shall be consumable by another block, so a workflow (TE-4) can wire them

Scenario: Create a verification block for a downstream system
  Given a downstream record to check (e.g. an ESB/SAP reconciliation feed)
  When a verification block is created
  Then it shall be defined to assert that record using a standard, parameterised check
  And it shall require no project-specific rewrite to reuse

Scenario: Set up a block to be idempotent
  Given a block that performs a state-changing action
  When the block is created
  Then it shall declare an idempotency key
  And duplicate execution shall not double-process the action
```

> **Test blocks to encode (v1):** Hybris (order / checkout) · OMS (Order Creation · Scheduling · Release · Fulfilment · Cancellation · Appeasement · Return/Refund) · Payment / Klarna (Klarna Order Creation · Authorize · Capture · Refund · Cancel) · Database verification · API invoke/assert · Call Centre actions · ESB/SAP feed verification · CARS reconciliation. Each is a parameterised, environment-agnostic asset — this library is the reusable product value.

---

### TE-4 — Test Workflow Composition

**Status:** Pending OQ-E1
**Functional Area:** Test Asset Development
**Slash Command:** `/create-test-workflow`
**Requirements:** R-2
**Depends on:** TE-3

> **Purpose:** TE-4 **orchestrates** the TE-3 blocks into an ordered, state-passing end-to-end **workflow** — defining the phase sequence, the state handed between blocks, and the inter-block synchronisation (waits, polling, retries, fallbacks, hard-fail gates). TE-3 builds the blocks; TE-4 orchestrates them into a flow; TE-5 executes that flow.

```text
As an Automation / Framework Engineer,
I want to assemble the reusable TE-3 blocks into an ordered end-to-end test workflow,
so that a complete scenario is defined once as a single repeatable flow that can be executed and reused,
without changing the blocks themselves.
```

**Example phase sequence** (Klarna single-shipment capture, from the runbooks):

| Phase | Block | Hand-off (state) |
|---|---|---|
| 1 | Klarna Order Creation | `authorizationId` |
| 2 | Sterling Order Inject (`createOrder`) | `OrderNo` · `OrderHeaderKey` |
| 3 | Schedule & Release (`scheduleOrder` + `releaseOrder`) | order in pick queue |
| 4 | ASN Shipment + Capture | `captureId` → `PaymentReference6` |
| 5 | Assertions (`getOrderList` + Klarna `capture_id` match) | verdict inputs |
| 6 | Downstream feed check (SalesPosting / `yfs_export`) | feed asserted |

**Workflow synchronisation strategies** the orchestration coordinates between blocks:

| Strategy | Purpose | Example from the suite |
|---|---|---|
| Fixed settle wait | Let async state settle before the next call | Wait 5s after shipment before capture |
| Decision gate | Gate the next phase on a condition | `processOrderPayments` up to 6× at 5s until `PaymentReference6` set |
| Long-service timeout | Tolerate slow backends | `SGTASNShipmentSyncService` up to 180s / attempt; SalesPosting feed up to 8×30s (~4 min) |
| Retry-with-fallback | Absorb ordering ambiguity | `ReleaseNo` 1↔2 swap; deadlock (`YFC0100`) up to 3× |
| Known-condition branch | Treat expected states correctly | `OMP10079` over-shipment → poll `getOrderList` directly, skip the capture call |
| Hard-fail gate | Stop on genuine errors | Any non-`OMP10079` error after fallbacks → stop immediately; no later phase runs |

> **Examples to try:** a workflow with a single block; reordering blocks; a phase with no gate declared; a branch that never triggers; a hard-fail on the first phase.

**Acceptance criteria:**

```gherkin
Scenario: Compose blocks into an ordered test workflow
  Given a set of TE-3 test blocks for a scenario
  When they are composed into a test workflow
  Then the workflow shall define the exact order in which the blocks run
  And the output of each block shall feed the input of the next

Scenario: Reorder or extend the workflow without changing the blocks
  Given an existing test workflow
  When a block is added, removed, or reordered in the workflow
  Then the workflow shall remain valid and runnable
  And no reusable TE-3 block shall require modification

Scenario: Workflow is handed to execution
  Given a completed test workflow for a scenario
  When it is passed to TE-5 for execution
  Then it shall run end-to-end as a single traceable sequence of blocks

Scenario: Workflow declares a synchronisation gate for an async phase
  Given a phase whose result is produced asynchronously
  When the workflow is composed
  Then the phase shall declare a settle wait and a decision gate (interval, bound, and success condition)
  And the next phase shall be declared to run only after that gate is satisfied

Scenario: Workflow declares a branch for a known non-error condition
  Given a phase that can return a known non-error signal (e.g. over-shipment / already-shipped)
  When the workflow is composed
  Then the workflow shall declare an alternate path for that condition
  And that condition shall be declared as non-failing
```

---

### TE-5 — Test-Script-Driven Execution

**Status:** Pending OQ-E1
**Functional Area:** Test Execution
**Slash Command:** `/execute-test`
**Requirements:** R-1 · R-9
**Artifacts:** `<tc>-e2e.test-script.ts` (test script)

> **Purpose:** TE-5 **executes** the TE-4 workflow (the composed TE-3 blocks) against a prepared environment and records the verdict. TE-4 defines the flow; TE-5 runs it.

> **Complex-story split:** TE-5 is de-risked by spike **SP-1** (harness decision); it delivers the actual execution functionality once SP-1 concludes.

```text
As a QA engineer,
I want to execute the TE-4 test workflow against a prepared environment,
comparing actual vs expected results,
so that each run produces a clear verdict
without modifying the workflow or the reusable blocks.
```

**Execution engine mechanics** — how the workflow is run:

- **Sequential phases, `workers=1`** — phases run strictly in order against shared UAT/Dev environments to avoid race conditions; each block's own waits and retries are honoured.
- **Timeouts & retries** — a per-phase timeout (configurable); an optional single retry on CI to absorb transient network flakiness.
- **Resilience** — honours the per-phase timeouts, so a slow-but-valid response is not a false failure; declared known-condition branches follow their alternate path.
- **State & recovery** — persists per-run test-case state so an interrupted run can be re-invoked; the run decides whether to restart from scratch or resume from the last completed phase (full mid-execution resume is a planned enhancement — see §9. Future Enhancements).
- **Telemetry** — records per-phase timings and a retry log, handed to TE-6 for the run log.
- **Verdict** — the assertions decide Pass/Fail; a mismatch is always a failure, never a warning.

> **Examples to try:** an interrupted run resumed vs restarted; a payment 5xx then a 4xx; a slow service near its timeout; the retry bound reached; re-running the same TC.

**Acceptance criteria:**

```gherkin
Scenario: Execute the workflow in its defined order
  Given a test workflow that lists TE-3 blocks in sequence
  When /execute-test runs
  Then the blocks shall execute in the exact order defined by the workflow
  And outputs of earlier blocks shall be available to later blocks

Scenario: Enforce the workflow's declared synchronisation at runtime
  Given a workflow whose phases declare settle waits, decision gates, and a known-condition branch (TE-4)
  When /execute-test runs it with workers=1
  Then phases shall execute strictly in the declared order
  And each declared decision gate shall be enforced (settle wait, then evaluate to its bound) before advancing
  And the per-phase timeouts shall be honoured so a slow-but-valid response is not treated as a failure
  And a declared known-condition shall follow its alternate path without failing
  And per-phase timings and any retries shall be captured for the run log

Scenario: Execute a test case to a Passed verdict
  Given a prepared environment (TE-2) and a test script for the case
  When the test case is executed via /execute-test
  Then each block shall run with its parameterised data
  And the actual result shall be compared against the expected results
  And on match the case shall be marked Passed with environment and timestamp

Scenario: Execution fails and is captured
  Given a test case executing against a target environment
  When an actual result does not match the expected result
  Then the case shall be marked Failed
  And the failing block, actual value, and evidence shall be captured
  And the failure shall be available to raise a defect downstream

Scenario: A payment operation fails and is safely held
  Given a workflow phase that calls a payment operation
  When the provider returns a network (5xx/timeout) or business (4xx) error
  Then a payment hold shall be applied to the order
  And the failure shall be routed to the named error queue for that operation
  And no partial success shall be recorded as Passed

Scenario: Retry budget is exhausted
  Given a decision gate with a bounded number of attempts
  When the condition is not met within the bound
  Then the case shall be marked Failed with the unmet condition named
  And no further attempts shall be made

Scenario: An interrupted run is re-invoked safely
  Given a test case that stopped mid-run with its state persisted
  When it is re-invoked
  Then the run shall decide whether to restart from scratch or resume from the last completed phase
  And it shall not leave the order in an inconsistent state
```

---

### TE-6 — Execution Result Capture & Zephyr Sync

**Status:** Pending OQ-E3
**Requirements:** R-8 · R-10
**Artifacts:** per-run Markdown log — `_run-logs/{TC-ID}/{TC-ID}_{yyyyMMdd}_{HHmm}_{RESULT}.md` (+ rolling `index.md`)
**Supports:** `/execute-test`

```text
As a QA lead,
I want every execution to write a per-run Markdown log (in `_run-logs/`) and produce a traceable result with evidence,
so that the log can drive telemetry, upload results to Zephyr, and log JIRA defects,
and test status is visible to the whole project team without manual reporting.
```

> **Boundary vs TE-5:** TE-5 *emits* per-phase timings, the retry log, and the verdict during the run; TE-6 *persists* them to the per-run Markdown log and *syncs* them to Zephyr / JIRA.

> **Examples to try:** Zephyr down at finish; a Pass vs Fail vs Blocked verdict; very large evidence; two concurrent runs writing logs.

**Acceptance criteria:**

```gherkin
Scenario: Record and sync a passed execution
  Given a test case that completes with all steps matching expected results
  When execution finishes
  Then a Passed verdict shall be recorded with environment and timestamp
  And the result shall be synced to the configured Zephyr test cycle

Scenario: Record evidence for a failed execution
  Given a test case that fails at a step
  When execution finishes
  Then logs, responses, and screenshots shall be persisted to the evidence store
  And the Failed verdict shall be synced to Zephyr with a link to the evidence

Scenario: Result sink unavailable does not lose the result
  Given the Zephyr endpoint is temporarily unavailable
  When an execution completes
  Then the result and evidence shall be persisted locally
  And shall be re-syncable once the endpoint is available

Scenario: Per-run log serves telemetry, result upload, and defect logging
  Given an execution that has completed
  Then a per-run Markdown log shall be written to `_run-logs/{TC-ID}/` capturing summary, phase timings, and assertions
  And a row shall be prepended to the rolling `_run-logs/index.md`
  And the log shall be used to upload the test-case result to the external tool (Zephyr)
  And on failure the log shall provide the detail used to log a JIRA defect
```

---

### TE-7 — Environment-Agnostic Configuration

**Status:** Ready
**Requirements:** R-7
**Supports:** `/execute-test` — *defining portability requirement*

```text
As an Onboarding Engineer adopting the product in a new project,
I want all environment, data, and credential details resolved from external configuration,
so that a new project can adopt the whole suite by changing configuration only —
accelerating onboarding and regression coverage instead of re-building tests.
```

> **Boundary vs TE-2:** TE-2 provisions a *specific* target environment for a given run; TE-7 is the *principle* that every environment, data, and credential is resolvable from external config, so the same assets move to any project unchanged.

> **Examples to try:** a missing config key; an invalid config value; a referenced secret that is absent; pointing the same assets at Project B.

**Acceptance criteria:**

```gherkin
Scenario: Same case executes in a different project by config only
  Given a test case and test script validated in Project A
  When the configuration is pointed at Project B's environment, data, and Zephyr
  Then the case shall execute against Project B
  And produce a result in Project B's Zephyr instance
  And no framework or test source code shall require modification

Scenario: Configuration validated before execution
  Given an execution configuration for a target environment
  When /execute-test starts
  Then required configuration keys shall be validated as present
  And execution shall be blocked with a clear message if any are missing
```

---

### Spikes (investigative stories)

> Per INVEST, items that block estimation are handled as timeboxed **spikes** — just enough research to make a decision, after which the affected story becomes estimable.

| Spike | Resolves | Goal | Timebox | Done when |
|---|---|---|---|---|
| **SP-1 — Execution harness decision** | OQ-E1 | Decide automation-harness vs manual test-script execution for `/execute-test` | 2 days | A recorded decision (with rationale) that lets TE-4 and TE-5 acceptance criteria be finalised |
| **SP-2 — Block invocation approach** | OQ-E2 | Decide API-level vs UI-level (or both) per system for reusable blocks | 2 days | A recorded per-system approach that lets TE-3 blocks be built without rework |

---

## 6. Story Traceability

| Story | Functional Area | Slash Command | Requirements | Depends On |
|---|---|---|---|---|
| TE-1 Local Machine Setup | Local Setup | `/setup-test-local` | R-11 | — |
| TE-2 Test Environment Setup | Environment Setup | `/setup-test-env` | R-3 · R-4 · R-5 | TE-1 |
| TE-3 Reusable Test Blocks (Multi-System) | Test Asset Development | `/create-test-block` | R-6 | — |
| TE-4 Test Workflow Composition | Test Asset Development | `/create-test-workflow` | R-2 | TE-3 |
| TE-5 Test-Script-Driven Execution | Test Execution | `/execute-test` | R-1 · R-9 | TE-2 · TE-4 · TE-6 · TE-7 |
| TE-6 Result Capture & Zephyr Sync | Test Execution | supports `/execute-test` | R-8 · R-10 | — |
| TE-7 Environment-Agnostic Config | Test Execution | supports `/execute-test` | R-7 | — |

**7 stories · 34 acceptance scenarios** — together they fully define the inputs and behaviour required for `/execute-test`.

---

## 7. Open Items Affecting Delivery

| ID | Story | Blocker | Owner | Impact |
|---|---|---|---|---|
| OQ-E1 | TE-5 | Automation harness vs manual test-script execution not yet confirmed | Test Lead | Changes TE-4/TE-5 acceptance criteria significantly — resolved via spike **SP-1** |
| OQ-E2 | TE-3 | Test blocks — API-level, UI-level, or both, per system? | Test Lead / Architect | Determines implementation approach for the library — resolved via spike **SP-2** |
| OQ-E3 | TE-6 | Zephyr write-back depth (results only vs results + evidence links) | QA Lead | Affects TE-6 sync scope |
| OQ-E4 | TE-2 | Test data strategy — synthetic seed vs environment snapshot | QA / Data | Affects data provisioning and cleanup design |

---

## 8. Non-Functional Criteria (testable)

> Non-functional requirements written so they are verifiable (INVEST: Testable), automated where possible.

| NFR | Requirement | How it's verified |
|---|---|---|
| Run-time budget | A single test case completes within its configured time budget (default 8 min) | Run-log phase timings vs the budget |
| Flakiness tolerance | A stable test case passes on ≥ 95% of consecutive runs against a healthy environment | Repeat-run report over N runs |
| Secrets handling | No credential, token, cert password, or `.p12` is embedded in any test asset or run log | Static scan of assets + logs; all secrets resolved from config |
| Data isolation | Concurrent runs by different engineers do not collide on test data | Tagged-data check across parallel runs |
| Portability | Switching project/environment needs a config change only, no code change | Diff shows only config changed between projects |

---

## 9. Future Enhancements

> Capabilities identified during design but out of scope for this slice — captured here so they are not lost.

| ID | Story | Enhancement | Rationale | Priority |
|---|---|---|---|---|
| FE-1 | TE-5 | **Mid-execution resume** — using the persisted per-run test-case state, restart an interrupted case from the last completed phase instead of from scratch | Avoids re-running costly earlier phases (e.g. order creation, capture) after a transient failure; cuts rerun time on long multi-phase cases | P2 |
