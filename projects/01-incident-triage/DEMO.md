# Five-minute demo

## Preparation

Run tests, then start a fresh mock database:

```bash
python3 -m unittest discover -s tests -v
python3 -m lab serve --db runtime/customer-demo-01.db
```

Use a new filename for each fresh demonstration. Open the printed browser URL. All names and knowledge articles are synthetic.

## 0:00–0:45 — Explain the problem

“Service desks spend time reading tickets, choosing queues, and preparing notes. This prototype makes an evidence-backed recommendation that a reviewer can inspect. Today it runs offline; no customer system is connected.”

## 0:45–2:00 — Routine incident

Select INC-LAB-001 and run triage. Show matched `vpn`, Network Support, P3 from explicit impact/urgency, KB-LAB-001, five-step trace, and the three proposed fields. Enter a reviewer name and approve the local update. Show the decision and audit trail.

“This gives us a repeatable handoff draft with the reason for routing. It saves the reviewer from recreating the draft in this example. Actual time savings must be measured in a pilot.”

## 2:00–3:00 — Policy boundaries

Select INC-LAB-004: P1 escalates and approval is disabled. Select INC-LAB-006: security escalates even though email also appears. Explain that this version produces an escalation recommendation; it does not notify a real team.

## 3:00–4:00 — Missing and ambiguous inputs

Select INC-LAB-005 and show missing information. Select INC-LAB-007 and show network/email ambiguity. Explain why the engine does not invent a priority or guess a group. Use a custom VPN preview and switch impact to Unknown to show a live response without record writes.

## 4:00–5:00 — Evidence and platform path

Download a result JSON and show the evaluation report. Explain 10/10 teaching cases as specification evidence, not production accuracy. Show the ServiceNow mapping checklist: verify dictionary choices, reference IDs, priority lookup, permissions, and Agent Studio availability before moving to a PDI.

Finish with: “We now have a working supervised baseline and tests. The next increment is to improve language handling and compare alternatives against this baseline, while keeping the write controls authoritative.”
