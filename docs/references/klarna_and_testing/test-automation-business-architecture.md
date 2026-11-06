# DMI-551 — Business Architecture
## UK Klarna BNPL Integration — Levels 1“6

> **Layer:** Business Architecture — stable decomposition from Enterprise to Business Rules
> **Jira:** [DMI-551](https://signetjewelers.atlassian.net/browse/DMI-551)
> **Status:** Draft
> **Companion TDD:** [tdd.md](../04-design/tdd.md)
> **Companion Product Management:** [requirements.md](./requirements.md)
> **Framework references:** [Business Architecture First Principles](../../../docs/knowledge/architecture/business-architecture-first-principles.md) · [Product Management Guidelines](../../../docs/knowledge/sdlc/product-management-guidelines.md)

This document captures the business architecture decomposition for DMI-551 across six levels: Enterprise → Value Streams → Business Functions → Sub-Functions → Business Capabilities → Business Rules (EARS). Level 7 (User Stories and acceptance criteria) is defined in `requirements.md`. This document is intended to merge into the TDD and serves as the stable traceability backbone for all implementation, testing, and governance artefacts.

---

## Table of Contents

- [1. Level 1 — Enterprise and Value Streams](#1-level-1--enterprise-and-value-streams)
- [2. Level 2 — Business Functions](#2-level-2--business-functions)
- [3. Level 3 — Sub-Functions](#3-level-3--sub-functions)
- [4. Level 4 — Business Capabilities](#4-level-4--business-capabilities)
- [5. Level 5 — Processes and Workflows](#5-level-5--processes-and-workflows)
- [6. Level 6 — Business Rules (EARS)](#6-level-6--business-rules-ears)
- [7. Traceability Summary](#7-traceability-summary)

---

## 1. Level 1 — Enterprise and Value Streams

**Enterprise:** Signet Jewelers UK — Ernest Jones (org 3000) · H. Samuel (org 4000)

| ID | Value Stream | TDD Functional Areas | Scope |
|---|---|---|---|
| VS-1 | **Order-to-Cash** | OC · OM&F · DS | Order placement → Klarna auth acknowledgment → Fulfilment → Payment capture → Cancellation handling → Settlement feeds to SAP CAR/S4 and CRDM |
| VS-2 | **Returns-to-Refund** | RET | Return authorisation → Refund execution (full, partial, appeasement) |

**Scope boundaries:**
- Hybris checkout and Klarna Payments API authorisation (pre-DOM) are upstream entry points to VS-1 — not in DOM scope
- Downstream reconciliation feeds (DS) are the settlement tail of VS-1 — not a separate value stream
- Cancellation flows (S3“S5, including release-remaining-auth) are exception paths within VS-1 / OM&F

---

## 2. Level 2 — Business Functions

| ID | Business Function | Value Stream(s) | TDD FA | What it covers in DMI-551 |
|---|---|---|---|---|
| BF-1 | **Order Management** | VS-1 | OC | Receiving order from Hybris via ESB; validating and acknowledging Klarna authorisation into Sterling |
| BF-2 | **Order Fulfilment** | VS-1 | OM&F | Shipment confirmation triggering capture; cancellation handling; release-remaining-auth at order conclusion |
| BF-3 | **Payment Processing** | VS-1, VS-2 | OM&F · RET | Capture, cancel, release-remaining-auth, refund — the payment event dispatch layer shared across both value streams |
| BF-4 | **Returns Management** | VS-2 | RET | Return order triggering refund; full, partial, and appeasement refund flows |
| BF-5 | **Financial Settlement** | VS-1 | DS | Post-capture/refund reconciliation feeds to SAP CAR/S4 and CRDM |

> BF-3 Payment Processing is a shared function invoked by both BF-2 and BF-4. The same `SGTUKCollectionOthersUE` dispatch handles capture (VS-1) and refund (VS-2). NFR cross-cutting concerns (error queues, idempotency, credentials, reliability) are quality attributes governing all five functions — they surface at the capability and rules levels.

---

## 3. Level 3 — Sub-Functions

### BF-1 — Order Management

| ID | Sub-Function | What it covers |
|---|---|---|
| SF-1.1 | **Order Intake and Validation** | Receiving `createOrder` XML from Hybris via ESB; validating `authorizationId` is present and non-blank (AR-003, S8) |
| SF-1.2 | **Payment Authorisation Acknowledgment** | Recording Klarna auth hold in Sterling on `AUTHORIZATION +ve` event; no Klarna API call made (S0) |

### BF-2 — Order Fulfilment

| ID | Sub-Function | What it covers |
|---|---|---|
| SF-2.1 | **Shipment Confirmation** | Triggering payment capture at shipment confirm event; single and multi-shipment flows (S1, S2) |
| SF-2.2 | **Order Cancellation** | Full cancellation before any capture (S3); cancel-after-partial-capture 403 handling (S4) |
| SF-2.3 | **Release Remaining Authorisation** | Order Closure event triggering release-remaining-auth at last-shipment conclusion; deferred from partial cancellation (S5, ADR-006) |

### BF-3 — Payment Processing

| ID | Sub-Function | What it covers |
|---|---|---|
| SF-3.1 | **Payment Event Dispatch** | `SGTUKCollectionOthersUE` routing by `paymentType` + `chargeType` + `requestAmount`; Klarna as `else if` branch (ADR-005) |
| SF-3.2 | **Klarna API Orchestration** | All Klarna API calls routed via AWS Orchestrator; DOM holds no credentials (ADR-008, ADR-002) |
| SF-3.3 | **Idempotency and Duplicate Prevention** | Deterministic `Idempotency-Key` (`{OrderId}-{ShipmentNumber}`) passed on every capture; Klarna deduplicates (CR-004) |
| SF-3.4 | **Payment Error Handling** | Transient failures → `SGT_PAYMENT_HOLD`; business exceptions (4xx) → named error queues; four dedicated `SGT_UK_KL_*` queues (ADR-003) |

### BF-4 — Returns Management

| ID | Sub-Function | What it covers |
|---|---|---|
| SF-4.1 | **Return Authorisation** | Return order raised in Sterling triggering `CHARGE -ve` payment event |
| SF-4.2 | **Refund Execution** | Full refund (S9), partial refund (S10), appeasement (S11); line-item level `order_lines` required (RF-001) |

### BF-5 — Financial Settlement

| ID | Sub-Function | What it covers |
|---|---|---|
| SF-5.1 | **Reconciliation Feed Generation** | Sterling Reconciliation Feed Service generating post-capture/refund invoice data (DS1, DS2) |
| SF-5.2 | **Downstream System Integration** | Feed routing via ESB (MuleSoft) → ESB (POS Cloud) → SAP CAR/S4 and CRDM; `TenderClass=Klarna`, `Order_Id`, `Capture_Id`, `Capture_Amount` (OQ-2 open) |

---

## 4. Level 4 — Business Capabilities

14 capabilities. Technology-agnostic, stable, verb+noun named.

### BF-1 — Order Management

| ID | Capability | Business Ability | Traces To |
|---|---|---|---|
| C-1.1 | **Validate Payment Intent** | Verify that a BNPL authorisation identifier exists and is valid before any payment operation proceeds | SF-1.1 · AR-003 · S8 |
| C-1.2 | **Acknowledge Payment Authorisation** | Record that a BNPL payment has been authorised by the provider and hold the authorised amount in the order management system | SF-1.2 · S0 |

### BF-2 — Order Fulfilment

| ID | Capability | Business Ability | Traces To |
|---|---|---|---|
| C-2.1 | **Capture Payment on Shipment** | Collect the authorised payment amount from the BNPL provider at the point of shipment confirmation | SF-2.1 · S1 · S2 |
| C-2.2 | **Cancel Payment Authorisation** | Reverse an uncaptured BNPL authorisation when an order is fully cancelled before shipment | SF-2.2 · S3 · S4 |
| C-2.3 | **Release Remaining Authorisation** | Release the unfulfilled portion of a BNPL authorisation at order conclusion when partial fulfilment has occurred | SF-2.3 · S5 · ADR-006 |

### BF-3 — Payment Processing

| ID | Capability | Business Ability | Traces To |
|---|---|---|---|
| C-3.1 | **Dispatch Payment Events** | Route payment lifecycle events (authorise, capture, cancel, refund) to the correct handler based on payment type and operation type | SF-3.1 · ADR-005 |
| C-3.2 | **Execute External Payment Operation** | Invoke the external BNPL provider's payment API through an integration layer for each payment operation | SF-3.2 · ADR-008 · ADR-002 |
| C-3.3 | **Ensure Payment Idempotency** | Prevent duplicate payment operations by generating and passing a deterministic operation key that the provider uses for deduplication | SF-3.3 · CR-004 |
| C-3.4 | **Handle Payment Failure** | Manage transient failures and business exceptions through payment holds and named error queues to ensure no silent failures and full operational visibility | SF-3.4 · ADR-003 · §7 |

### BF-4 — Returns Management

| ID | Capability | Business Ability | Traces To |
|---|---|---|---|
| C-4.1 | **Authorise Return** | Accept and record a customer return request, triggering the downstream refund payment event | SF-4.1 · RET |
| C-4.2 | **Execute Payment Refund** | Return the captured payment amount (full, partial, or appeasement) to the customer through the BNPL provider at line-item level | SF-4.2 · S9 · S10 · S11 · RF-001 |

### BF-5 — Financial Settlement

| ID | Capability | Business Ability | Traces To |
|---|---|---|---|
| C-5.1 | **Generate Payment Reconciliation Feed** | Produce structured post-capture and post-refund settlement data for consumption by downstream financial systems | SF-5.1 · DS1 · DS2 |
| C-5.2 | **Publish Settlement Data to Financial Systems** | Deliver payment settlement information — including payment type, order identifier, capture identifier, and amount — to reconciliation, reporting, and accounting systems | SF-5.2 · OQ-2 · DS |

---

## 5. Level 5 — Processes and Workflows

24 processes. Each traces to one or more TDD scenarios.

### C-1.1 — Validate Payment Intent

| ID | Process | Flow | TDD Ref |
|---|---|---|---|
| P-1.1.1 | **Guard: Check authorisation identifier at charge event** | When a CHARGE event fires, check `authorizationId` is present and non-blank before any API call. If null/blank → order MUST FAIL → route to capture error queue. Must NOT place on hold. | S8 · AR-003 |

### C-1.2 — Acknowledge Payment Authorisation

| ID | Process | Flow | TDD Ref |
|---|---|---|---|
| P-1.2.1 | **Record auth hold on AUTHORIZATION +ve** | `chargeType=AUTHORIZATION, requestAmount > 0` → set `authorizationAmount = requestAmount`, `retryFlag=N`. No Klarna API call. | S0 |

### C-2.1 — Capture Payment on Shipment

| ID | Process | Flow | TDD Ref |
|---|---|---|---|
| P-2.1.1 | **Single-shipment full capture** | Confirm Shipment fires `CHARGE +ve` → convert amount to pence → send capture request via orchestrator → on 201: store `capture_id` in `paymentReference6`, close CTR | S1 |
| P-2.1.2 | **Multi-shipment partial capture** | Same as P-2.1.1, fired once per shipment. Klarna tracks running balance across captures. DOM makes one call per shipment with no balance tracking required. | S2 |

### C-2.2 — Cancel Payment Authorisation

| ID | Process | Flow | TDD Ref |
|---|---|---|---|
| P-2.2.1 | **Full cancel before any capture** | `AUTHORIZATION -ve`, no prior capture → send cancel request → on 204: close CTR, no holds | S3 |
| P-2.2.2 | **Cancel after partial capture (403 path)** | `AUTHORIZATION -ve`, capture exists → Klarna returns 403 → apply `ATTR_PAYMENT_ERROR_HOLD` → route to `SGT_UK_KL_CANCEL_PAYMENT_ERROR_QUEUE`. Do not retry. Do not route to refund. | S4 · CL-002 |

### C-2.3 — Release Remaining Authorisation

| ID | Process | Flow | TDD Ref |
|---|---|---|---|
| P-2.3.1 | **Release remaining auth at order conclusion** | Order Closure event fires at last-shipment conclusion → captures list non-empty → send release-remaining-auth request → on 204: close CTR, no holds. Fires exactly once per order. | S5 · ADR-006 |

### C-3.1 — Dispatch Payment Events

| ID | Process | Flow | TDD Ref |
|---|---|---|---|
| P-3.1.1 | **Route by paymentType → chargeType → requestAmount** | UE invoked → `paymentType == Klarna?` → `chargeType?` → `requestAmount sign?` → dispatch to correct operation handler | §5.2 decision tree · ADR-005 |

### C-3.2 — Execute External Payment Operation

| ID | Process | Flow | TDD Ref |
|---|---|---|---|
| P-3.2.1 | **Invoke capture via orchestrator** | Build capture payload (pence amount + `order_lines`) → POST to orchestrator → orchestrator forwards to Klarna `/captures` | S1 · S2 |
| P-3.2.2 | **Invoke cancel via orchestrator** | Build cancel request (empty body) → POST to orchestrator → orchestrator forwards to Klarna `/cancel` | S3 · S4 |
| P-3.2.3 | **Invoke release-remaining-auth via orchestrator** | Build release request (empty body) → POST to orchestrator → orchestrator forwards to Klarna `/release-remaining-authorization` | S5 |
| P-3.2.4 | **Invoke refund via orchestrator** | Build refund payload (pence amount + line-level `order_lines`) → POST to orchestrator → orchestrator forwards to Klarna `/refunds` | S9 · S10 · S11 · RF-001 |

### C-3.3 — Ensure Payment Idempotency

| ID | Process | Flow | TDD Ref |
|---|---|---|---|
| P-3.3.1 | **Generate and pass idempotency key** | For every capture request, generate deterministic key `{OrderId}-{ShipmentNumber}` → pass as `Idempotency-Key` header → reuse same key on retry | CR-004 |

### C-3.4 — Handle Payment Failure

| ID | Process | Flow | TDD Ref |
|---|---|---|---|
| P-3.4.1 | **Handle transient failure (5xx / timeout)** | Any 5xx or connection timeout → apply `SGT_PAYMENT_HOLD` → route to `SGT_UK_KL_NETWORK_ERROR_PAYMENT_QUEUE` → ops investigates | S6 · S12 · S13 · S14 |
| P-3.4.2 | **Handle business exception (4xx)** | 4xx response → apply `ATTR_PAYMENT_ERROR_HOLD` → route to operation-specific error queue → no retry → manual resolution | S4 · S7 · S15 · §7 |

### C-4.1 — Authorise Return

| ID | Process | Flow | TDD Ref |
|---|---|---|---|
| P-4.1.1 | **Raise return order and trigger refund event** | Return order raised in Sterling → `CHARGE -ve` payment event fires → dispatch to refund handler | S9“S11 |

### C-4.2 — Execute Payment Refund

| ID | Process | Flow | TDD Ref |
|---|---|---|---|
| P-4.2.1 | **Full refund after full capture** | `CHARGE -ve` full amount → refund request with `order_lines` → on 200: close CTR, `refund_id` returned (audit only), `paymentReference6` retains `capture_id` | S9 · RF-001 |
| P-4.2.2 | **Partial refund after multi-shipment** | `CHARGE -ve` partial amount → refund request with affected `order_lines` → on 200: close CTR. Klarna distributes across captures automatically. | S10 · RF-001 |
| P-4.2.3 | **Appeasement refund** | `CHARGE -ve` goodwill amount → same Klarna refund API → on 200: close CTR. No separate appeasement API. | S11 · RF-003 |

### C-5.1 — Generate Payment Reconciliation Feed

| ID | Process | Flow | TDD Ref |
|---|---|---|---|
| P-5.1.1 | **Generate post-capture feed** | Capture confirmed (201) → Sterling Reconciliation Feed Service produces invoice data with `TenderClass=Klarna`, `capture_id`, `Capture_Amount` | DS1 |
| P-5.1.2 | **Generate post-refund feed** | Refund confirmed (200) → feed updated with refund amount reflected | DS2 |

### C-5.2 — Publish Settlement Data to Financial Systems

| ID | Process | Flow | TDD Ref |
|---|---|---|---|
| P-5.2.1 | **Route settlement feed to SAP and CRDM** | Invoice data → ESB (MuleSoft) → ESB (POS Cloud) → SAP CAR/S4 + CRDM with `PaymentType=Klarna`, `Order_Id`, `Capture_Id`, `Capture_Amount` (OQ-2 field names open) | DS1 · DS2 · OQ-2 |

---

## 6. Level 6 — Business Rules (EARS)

32 rules. EARS syntax throughout — each rule is atomic, declarative, and technology-agnostic.

### C-1.1 — Validate Payment Intent

| ID | EARS Pattern | Rule |
|---|---|---|
| BR-1.1.1 | Event-Driven | When a payment capture event is triggered, the system shall verify that a BNPL authorisation identifier is present and non-blank before invoking any payment operation |
| BR-1.1.2 | Unwanted Behaviour | If the authorisation identifier is null or blank at capture time, the system shall fail the order and route it to the capture error queue — the order shall NOT be placed on a payment hold |

### C-1.2 — Acknowledge Payment Authorisation

| ID | EARS Pattern | Rule |
|---|---|---|
| BR-1.2.1 | Event-Driven | When an authorisation event with a positive amount is received, the system shall record the authorised amount against the order without invoking any external payment provider API |
| BR-1.2.2 | Ubiquitous | The system shall set the retry flag to N on authorisation acknowledgment |

### C-2.1 — Capture Payment on Shipment

| ID | EARS Pattern | Rule |
|---|---|---|
| BR-2.1.1 | Event-Driven | When a shipment is confirmed, the system shall submit a payment capture request to the BNPL provider for the shipment amount |
| BR-2.1.2 | Event-Driven | When a capture is confirmed by the provider, the system shall store the provider-returned capture identifier against the payment record and close the payment transaction |
| BR-2.1.3 | Ubiquitous | The system shall convert all monetary amounts to minor currency units (pence) before submitting to the payment provider, using rounding — never truncation |
| BR-2.1.4 | Ubiquitous | The system shall submit one capture request per shipment invoice — never one aggregated capture per order |
| BR-2.1.5 | Unwanted Behaviour | If the capture amount exceeds the authorised amount, the system shall apply a payment error hold and route the payment to the capture error queue without invoking the provider API |

### C-2.2 — Cancel Payment Authorisation

| ID | EARS Pattern | Rule |
|---|---|---|
| BR-2.2.1 | Event-Driven | When an order cancellation is triggered and no prior capture exists, the system shall submit a full authorisation cancellation request to the BNPL provider |
| BR-2.2.2 | Unwanted Behaviour | If the provider returns a 403 response on a cancellation request, the system shall apply a payment error hold and route the payment to the cancel error queue — the system shall NOT retry and shall NOT route to refund |

### C-2.3 — Release Remaining Authorisation

| ID | EARS Pattern | Rule |
|---|---|---|
| BR-2.3.1 | Event-Driven | When the last shipment in an order is concluded and at least one prior capture exists, the system shall submit a release-remaining-authorisation request to the BNPL provider |
| BR-2.3.2 | Ubiquitous | The system shall submit the release-remaining-authorisation request exactly once per order at order conclusion — never per cancelled line |
| BR-2.3.3 | State-Driven | While an order has no captures, the system shall use authorisation cancellation (not release-remaining-authorisation) to reverse the full authorised amount |

### C-3.1 — Dispatch Payment Events

| ID | EARS Pattern | Rule |
|---|---|---|
| BR-3.1.1 | Event-Driven | When a payment event is received, the system shall route it based on payment type, charge type, and request amount sign — in that order |
| BR-3.1.2 | Ubiquitous | The system shall process Klarna payment events within the existing BNPL payment dispatch handler as a named branch — no separate handler registration is required |

### C-3.2 — Execute External Payment Operation

| ID | EARS Pattern | Rule |
|---|---|---|
| BR-3.2.1 | Ubiquitous | The system shall route all BNPL provider API calls through the integration orchestration layer — the order management system shall hold no provider credentials |
| BR-3.2.2 | Ubiquitous | The system shall include line-item detail in all capture and refund requests submitted to the provider |
| BR-3.2.3 | Ubiquitous | The system shall use the authorisation identifier as the primary provider order reference for all downstream payment operations |

### C-3.3 — Ensure Payment Idempotency

| ID | EARS Pattern | Rule |
|---|---|---|
| BR-3.3.1 | Ubiquitous | The system shall generate a deterministic idempotency key per payment operation in the format `{OrderId}-{ShipmentNumber}` and submit it with every capture request |
| BR-3.3.2 | Ubiquitous | The system shall reuse the same idempotency key on retries of the same operation — the key shall never be regenerated for a retry |

### C-3.4 — Handle Payment Failure

| ID | EARS Pattern | Rule |
|---|---|---|
| BR-3.4.1 | Unwanted Behaviour | If the payment provider or integration layer returns a 5xx response or connection timeout, the system shall apply a payment hold and route to the network error queue — no operation-specific retry shall be attempted by the order management system |
| BR-3.4.2 | Unwanted Behaviour | If the payment provider returns a 4xx response (business exception), the system shall apply a payment error hold and route to the operation-specific error queue — the system shall NOT retry automatically |
| BR-3.4.3 | Ubiquitous | The system shall route capture failures, cancel failures, refund failures, and network failures to separate named error queues to enable per-operation operational visibility |
| BR-3.4.4 | Ubiquitous | The system shall not proceed with any payment operation if a prior unresolved payment hold exists on the order |

### C-4.2 — Execute Payment Refund

| ID | EARS Pattern | Rule |
|---|---|---|
| BR-4.2.1 | Event-Driven | When a return order is raised, the system shall submit a refund request to the provider at line-item level specifying the returned items |
| BR-4.2.2 | Ubiquitous | The system shall retain the capture identifier in the payment record after a refund — the capture identifier shall not be overwritten by a refund identifier |
| BR-4.2.3 | Ubiquitous | The system shall use the standard refund operation for appeasement credits — no separate appeasement payment API shall be invoked |

### C-5.1 — Generate Payment Reconciliation Feed

| ID | EARS Pattern | Rule |
|---|---|---|
| BR-5.1.1 | Event-Driven | When a payment capture is confirmed, the system shall generate a reconciliation feed record including the payment type, order identifier, capture identifier, and captured amount |
| BR-5.1.2 | Event-Driven | When a payment refund is confirmed, the system shall update the reconciliation feed to reflect the refunded amount |

### C-5.2 — Publish Settlement Data to Financial Systems

| ID | EARS Pattern | Rule |
|---|---|---|
| BR-5.2.1 | Ubiquitous | The system shall classify all Klarna payment records with the agreed BNPL tender classification in all outbound feeds to financial and reporting systems |

---

## 7. Traceability Summary

Full hierarchy from Enterprise to Business Rules (L1“L6). Each row is one capability — the stable anchor all other levels trace through. For Level 7 (User Stories), see `requirements.md`.

| L1 Value Stream | L2 Business Function | L3 Sub-Function | L4 Capability | L5 Processes | L6 Business Rules | TDD Scenarios |
|---|---|---|---|---|---|---|
| VS-1 Order-to-Cash | BF-1 Order Management | SF-1.1 Order Intake and Validation | C-1.1 Validate Payment Intent | P-1.1.1 — Guard: check `authorizationId` is present and non-blank before any API call | BR-1.1.1“BR-1.1.2 — Non-blank auth ID required; null/blank → fail order to capture error queue (not a hold) | S8 |
| VS-1 Order-to-Cash | BF-1 Order Management | SF-1.2 Payment Authorisation Acknowledgment | C-1.2 Acknowledge Payment Authorisation | P-1.2.1 — Record auth hold on `AUTHORIZATION +ve` event; no Klarna API call made | BR-1.2.1“BR-1.2.2 — Store authorised amount without calling provider; set retry flag = N | S0 |
| VS-1 Order-to-Cash | BF-2 Order Fulfilment | SF-2.1 Shipment Confirmation | C-2.1 Capture Payment on Shipment | P-2.1.1“P-2.1.2 — One capture request per shipment (single and multi-shipment); store `capture_id` on 201 | BR-2.1.1“BR-2.1.5 — Capture on shipment confirm; convert to pence; one call per shipment invoice; amount must not exceed auth | S1 · S2 |
| VS-1 Order-to-Cash | BF-2 Order Fulfilment | SF-2.2 Order Cancellation | C-2.2 Cancel Payment Authorisation | P-2.2.1“P-2.2.2 — Full cancel if no prior capture; 403 after partial capture → error hold, error queue, no retry | BR-2.2.1“BR-2.2.2 — Cancel full auth when no captures exist; 403 response → error hold + cancel queue, never retry or route to refund | S3 · S4 |
| VS-1 Order-to-Cash | BF-2 Order Fulfilment | SF-2.3 Release Remaining Authorisation | C-2.3 Release Remaining Authorisation | P-2.3.1 — Fire release-remaining-auth once at order conclusion when at least one capture exists | BR-2.3.1“BR-2.3.3 — Exactly once at order conclusion; never per cancelled line; if no captures exist, use cancel instead | S5 |
| VS-1 · VS-2 (shared) | BF-3 Payment Processing | SF-3.1 Payment Event Dispatch | C-3.1 Dispatch Payment Events | P-3.1.1 — Route by `paymentType` → `chargeType` → `requestAmount` sign; Klarna handled as named branch in existing UE | BR-3.1.1“BR-3.1.2 — Route in strict priority order (type, charge, amount sign); reuse existing BNPL handler, no new registration | §5.2 |
| VS-1 · VS-2 (shared) | BF-3 Payment Processing | SF-3.2 Klarna API Orchestration | C-3.2 Execute External Payment Operation | P-3.2.1“P-3.2.4 — Capture, cancel, release-remaining-auth, and refund all routed via AWS Orchestrator; DOM holds no credentials | BR-3.2.1“BR-3.2.3 — All provider calls via orchestration layer; include line-item detail on capture and refund; use auth ID as provider order reference | S1“S5 · S9“S11 |
| VS-1 · VS-2 (shared) | BF-3 Payment Processing | SF-3.3 Idempotency and Duplicate Prevention | C-3.3 Ensure Payment Idempotency | P-3.3.1 — Generate deterministic key `{OrderId}-{ShipmentNumber}`; pass on every capture; reuse same key on retry | BR-3.3.1“BR-3.3.2 — Deterministic key generated once per operation; never regenerated on retry; provider deduplicates using this key | CR-004 |
| VS-1 · VS-2 (shared) | BF-3 Payment Processing | SF-3.4 Payment Error Handling | C-3.4 Handle Payment Failure | P-3.4.1“P-3.4.2 — 5xx/timeout → payment hold + network error queue; 4xx → error hold + operation-specific queue; no automatic retry | BR-3.4.1“BR-3.4.4 — 5xx → network queue; 4xx → op-specific queue; four separate queues for capture/cancel/refund/network; blocked if prior hold exists | S6 · S7 · S12“S15 |
| VS-2 Returns-to-Refund | BF-4 Returns Management | SF-4.1 Return Authorisation | C-4.1 Authorise Return | P-4.1.1 — Raise return order in Sterling; triggers `CHARGE -ve` payment event to refund handler | — | S9“S11 |
| VS-2 Returns-to-Refund | BF-4 Returns Management | SF-4.2 Refund Execution | C-4.2 Execute Payment Refund | P-4.2.1“P-4.2.3 — Full, partial, and appeasement refunds via same Klarna refund API with line-item `order_lines` | BR-4.2.1“BR-4.2.3 — Refund at line-item level; retain `capture_id` after refund (never overwrite); use standard refund API for appeasement | S9 · S10 · S11 |
| VS-1 Order-to-Cash | BF-5 Financial Settlement | SF-5.1 Reconciliation Feed Generation | C-5.1 Generate Payment Reconciliation Feed | P-5.1.1“P-5.1.2 — Generate feed on capture confirm (201) and update on refund confirm (200); includes `TenderClass`, `capture_id`, amount | BR-5.1.1“BR-5.1.2 — Feed generated on capture confirm with payment type, order ID, capture ID, amount; updated on refund confirm | DS1 · DS2 |
| VS-1 Order-to-Cash | BF-5 Financial Settlement | SF-5.2 Downstream System Integration | C-5.2 Publish Settlement Data to Financial Systems | P-5.2.1 — Route feed via ESB (MuleSoft) → ESB (POS Cloud) → SAP CAR/S4 and CRDM; field names subject to OQ-2 | BR-5.2.1 — All Klarna records classified with agreed BNPL tender classification in all outbound feeds | DS1 · DS2 · OQ-2 |


