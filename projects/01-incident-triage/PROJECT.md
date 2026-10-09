# Project 01 — Incident triage prototype

## Customer problem and application

A service desk receives incomplete tickets and spends time selecting the right queue, locating guidance, and preparing internal notes. In a real implementation, evidence-backed recommendations could shorten initial handling and avoid some preventable handoffs. This lab demonstrates that workflow with controlled synthetic examples.

Example: “VPN unavailable” with impact 2/urgency 2 produces Network Support, suggested P3, VPN intake guidance, and an internal-note draft. A reviewer approves a local update. An incomplete “Something is broken” ticket asks for details, rather than inventing a route or priority.

## Scope

| Included in this iteration | Later work |
|---|---|
| Rules-based classification and routing | Model-assisted classification with held-out evaluation |
| Explicit numerical priority lookup | Instance-specific priority parity |
| Synthetic knowledge suggestions | Permission-aware live knowledge retrieval |
| Human approval and local mock updates | Authenticated ServiceNow review/write workflow |
| Security/high-priority escalation recommendation | Platform specialist workflow and notifications |
| Tests, trace, audit, visual demo | Live acceptance tests and measured customer outcomes |

## Baseline policy

| Impact / Urgency | 1 · High | 2 · Medium | 3 · Low |
|---|---|---|---|
| 1 · High | P1 | P2 | P3 |
| 2 · Medium | P2 | P3 | P4 |
| 3 · Low | P3 | P4 | P5 |

Security terms or P1/P2 always escalate, even if other fields are missing. Otherwise missing impact/urgency, no route, or multiple routes require clarification. A single non-security route with known P3/P4/P5 awaits human approval. There is no automatic write mode.

## Test design

Ten explicit teaching cases cover network/email/hardware, major incident priority, incomplete inputs, security precedence, ambiguous routing, description instructions, and missing impact. Independent expected outputs are checked separately from the implementation. Behavioral tests also cover all nine matrix cells, invalid types, input immutability, no writes before approval, rejection, revision conflicts, policy changes, persistence, duplicate and concurrent approvals, and HTTP behavior.

## Value measurement plan

Before claiming improvement, collect representative de-identified and authorized cases and reviewer ground truth. Separate tuning cases from a held-out evaluation set.

| Measure | How to assess |
|---|---|
| Routing agreement | Predicted group vs independently reviewed group on held-out cases |
| Clarification quality | Reviewer judgment of questions, completeness, and unnecessary questions |
| Escalation recall | Known high-risk cases correctly escalated; include false-negative analysis |
| First handling time | Timed manual vs assisted handling of matched cases, including review/correction |
| Correction/reassignment | Wrong suggestions and extra handoffs before/after pilot |
| Approval workload | Accepted, changed, and rejected proposals plus reviewer time |
| Runtime/model cost | Tool latency and cost if a model is introduced |

Report sample sizes and limitations. The supplied synthetic evaluation has no real customer time or financial data.

## Backlog and multi-project path

| Project | Deliverable | Customer application |
|---|---|---|
| 00A (now) | Offline foundation | Repeatable learning and controlled prototyping |
| 01 (now) | Incident triage baseline | Initial queue selection and note preparation |
| 01B | Model-assisted triage comparison | Handle varied language while measuring added value |
| 02 | Knowledge recommendation and draft resolution | Help analysts find approved guidance faster |
| 03 | Related incident clustering | Surface possible shared outages for human investigation |
| 04 | Change risk review | Provide evidence for reviewer decisions |
| 05 | Customer value dashboard | Demonstrate correction rates, review effort, and measured outcomes |
| 00B (when PDI returns) | Platform parity and access checks | Validate real schema, permissions, and orchestration capabilities |

Next implementation step: improve ambiguity handling and expand held-out fixtures before adding a model. A customer-facing prototype should remain supervised until its actual policy and integration controls are verified.
