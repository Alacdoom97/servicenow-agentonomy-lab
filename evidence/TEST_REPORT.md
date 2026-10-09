# Verification report

Verified 2026-10-09 with Python 3.12.14.

- Python standard-library unittest suite: **26 tests passed**.
- Explicit teaching-case evaluation: **10/10 passed**.
- Priority lookup: all nine configured impact/urgency combinations passed.
- Mock approval: field allowlist, no write before approval, rejection, stale revision and policy checks, idempotency, concurrent approvals, persistence, and audit passed.
- HTTP integration: UI response, health, complete triage-to-approved-record workflow, custom preview, invalid input, oversized input, and cross-origin rejection passed.
- No live ServiceNow or AI Agent Studio test was possible: PDI unavailable, AI access unknown.
- Rendered browser verification was not completed: this execution environment has no installed browser binary. The user-facing visual demo needs a local browser check using the checklist below.

## Browser check on your computer

1. Start the Python server and open the printed URL. Confirm ten incident choices load.
2. Run INC-LAB-001, enter a reviewer, approve, and inspect the audit.
3. Run INC-LAB-004 and INC-LAB-006; confirm approval is disabled.
4. Run INC-LAB-005 and INC-LAB-007; confirm clarification is visible.
5. Submit a custom VPN preview with impact/urgency 3/3; confirm P5 and no approval action.
6. Resize to a mobile width; confirm labels, cards, and buttons remain readable.
7. Open visual/offline-snapshot.html without the server; select a case and inspect results. Confirm custom preview and approval are disabled.
8. Download result JSON and check that its incident number matches the displayed result.

These are synthetic specification checks, not a production accuracy or customer value claim.
