# ServiceNow mapping and re-entry plan

Verified against official ServiceNow documentation on 2026-10-09. Release names, menus, installed applications, roles, and entitlements can differ on your eventual PDI. No instance access has been verified.

## Mapping

| Offline component | Intended ServiceNow mapping | What to validate on the instance |
|---|---|---|
| Synthetic JSON incident | `incident` table | Dictionary, required fields, business rules, existing ACLs |
| Lab impact/urgency | Incident impact/urgency choices | Actual choice values and organizational definitions |
| Lab matrix | Incident priority lookup rules | Actual configured mapping; platform derives priority |
| Group display label | Assignment group reference | Approved `sys_user_group` records and their `sys_id` values |
| Lab category label | Incident category choices | Customer-specific valid choices; `security` is a lab label |
| Synthetic knowledge | Approved knowledge content | Published state, access permissions, and relevance |
| Pure Python workflow | Flow Designer/subflow or AI Agent Studio workflow, if available | Tools, access, triggers, output contracts, and policy enforcement |
| Mock approval | Approved platform review mechanism | Authenticated reviewer, authorized role, audit, and concurrency semantics |
| Mock audit | Platform-supported execution/audit evidence | Retention, access, correlation, and integrity |
| SQLite adapter | Future ServiceNow adapter | Narrow reads/writes, authentication, ACLs, errors, and concurrency |

The lab matrix is an explicit teaching configuration. ServiceNow documents impact/urgency priority lookup rules as organizational configuration, so inspect the rules rather than assume this matrix is your instance's matrix.

Do not send lab group names or synthetic IDs straight to reference fields. Build a validated mapping to real records. Normalize numeric choice strings at the adapter boundary. Work notes are internal journal entries and need a deliberate access and append strategy. Do not force priority, resolve tickets, close incidents, or change infrastructure in the first live iteration.

## PDI return checklist — Project 00B

1. Record the instance release, availability, and relevant roles using your actual account. Use synthetic records only.
2. Confirm the Incident table and dictionary fields, category choices, assignment groups, impact/urgency choices, and priority lookup behavior.
3. Check whether AI Agent Studio is visible and which supporting applications and roles are present. Absence from navigation alone is not proof of entitlement status.
4. Verify plugin availability and entitlement before planning Agent Studio execution. A PDI does not establish that a licensed AI capability is available.
5. Create a small controlled set of synthetic incidents and real lab-only groups if permitted. Record their IDs in an environment-specific mapping, not in the generic engine.
6. Validate a read-only integration first with least-privilege access. Check field access and error behavior. Record platform priority results for the nine matrix combinations.
7. Compare the same synthetic cases with the offline engine; reconcile dictionary and business-rule differences.
8. Add one reviewer-approved write path after the read-only stage passes. Re-read before writing; design platform-side race prevention rather than assuming a pre-read is atomic. Test ACL rejection, concurrent changes, duplicate requests, rollback, and audit attribution.
9. If Agent Studio is available, reproduce the bounded workflow using its supported tools and test interface. If unavailable, learn platform orchestration with supported flows and keep the AI capability decision open.

## Primary sources

- [Define priority lookup rules](https://www.servicenow.com/docs/r/it-service-management/incident-management/def-prio-lookup-rules.html): priority is configured from impact and urgency.
- [AI Agent Studio](https://www.servicenow.com/docs/r/intelligent-experiences/aias-landing.html): centralized creation, configuration, and orchestration of agentic experiences.
- [AI agents library](https://www.servicenow.com/docs/r/intelligent-experiences/ai-agent-landing-page.html): agent availability depends on licenses, installed plugins, and roles.
- [Dot-walking in the REST Table API](https://developer.servicenow.com/blog.do?p=%2Fpost%2Fdot-walking-in-the-rest-table-api-2%2F): incident Table API reads and selecting returned fields.

These sources inform the mapping; they do not confirm any feature or license on your unavailable PDI. This package contains no live ServiceNow adapter, deployable platform update set, or certified integration.
