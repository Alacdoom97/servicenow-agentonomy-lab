# Project 00A — Offline foundation

## Goal

Create a repeatable development environment while the PDI is unavailable. Learn the boundaries that turn recommendations into controlled actions, and produce reusable artifacts for the multi-project lab.

## Delivered

- Python 3.10+ package using only the standard library.
- Synthetic incident/knowledge data and configurable lab policy.
- Mock persistence, approval, audit, revision checking, and API contracts.
- CLI environment report, local visual demo, portable snapshot, evaluation, and behavioral tests.
- Architecture, step-by-step build walkthrough, demo narrative, and platform re-entry checklist.

## Acceptance criteria

| Criterion | Evidence |
|---|---|
| Runs without a PDI, API key, or AI Agent Studio | `python3 -m lab doctor` and source adapter |
| Repeatable behavior for known inputs | Golden-case evaluation and deterministic output test |
| Incident is unchanged before approval | Store test |
| No ordinary approval for high-risk/incomplete cases | Engine and store tests |
| Repeated approved request writes once | Idempotency and concurrent approval tests |
| Changes and reviewer decisions are inspectable | Audit API and demo |
| Learner can explain the system | Learning log and architecture walkthrough |

## Decisions

Use deterministic rules first for inspectable behavior. Use explicit impact/urgency inputs rather than prose-based inference. Use a local adapter and three-field allowlist. Keep all sample data synthetic. Keep the visual interface thin so Python stays authoritative. Approval only changes local records.

These are working implementation choices for this offline continuation; Project 00A's earlier detailed scope was not available in the supplied conversation.

## Complete when

You can run the foundation checks, trace one scenario through all five steps, identify the policy gate, and explain what must be verified when the PDI returns.
