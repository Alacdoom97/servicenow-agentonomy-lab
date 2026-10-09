# Our first working session

## Step 1 — Project 00A environment checks

Open a terminal in the project root and run:

```bash
python3 --version
python3 -m lab doctor
```

Pass when Python is 3.10+ and the report lists offline mode, ten fixtures, zero external dependencies, and `live_servicenow_calls: false`. Your PDI remains unavailable; AI Agent Studio remains unknown. Doctor reports those recorded constraints; it does not query your ServiceNow account.

If Python cannot be found, use your existing Python 3 interpreter or install Python 3.10+ on your own computer. Do not install ServiceNow plugins or provide credentials for this step.

## Step 2 — Read the architecture

Read `docs/ARCHITECTURE.md`. Locate `triage()` in `lab/engine.py`, `Store.run()` and `Store.decide()` in `lab/store.py`, and the API handlers in `lab/server.py`.

Explain these boundaries aloud: the engine recommends; the policy decides whether ordinary review is possible; the adapter stores; a human approves; an audit records the transition. Ask yourself which boundary must remain authoritative when a model is added.

## Step 3 — Inspect one incident and its result

```bash
python3 -m lab demo --number INC-LAB-001
```

Expected: network, Network Support, P3, `awaiting_approval`, matched term `vpn`, KB-LAB-001, and five trace steps. The input gives impact 2 and urgency 2, so the engine uses the lab matrix. It does not guess these from “remote staff”.

Open `config/policy.json` and `data/incidents.json`. Change nothing on the first run. Identify where routing, urgency, impact, and policy live.

## Step 4 — Run verification

```bash
python3 -m unittest discover -s tests -v
python3 -m lab evaluate
```

Expected: all tests pass; evaluation passes 10/10 teaching cases. Test count may grow as we extend the lab. `data/expected.json` is the explicit oracle; do not automatically regenerate expected answers from the engine.

## Step 5 — Start the visual prototype

```bash
python3 -m lab serve
```

Open http://127.0.0.1:8765. Select INC-LAB-001, then **Run triage**. Inspect the matched term, knowledge article, proposed fields, and trace. Before approval, the record remains unchanged.

Enter your reviewer name and click **Approve local update**. The audit should contain `triage_proposed` and `review_approve`. The mock record changes category/group/work notes; it retains impact and urgency. There is no ServiceNow write.

## Step 6 — Exercise the policy gates

| Incident | Expected behavior | Discussion |
|---|---|---|
| INC-LAB-004 | P1; escalation; approval disabled | Why must a major incident be reviewed separately? |
| INC-LAB-005 | Missing details; clarification | Why should unknown priority remain unknown? |
| INC-LAB-006 | Security specialist escalation | Why does security take precedence over email routing? |
| INC-LAB-007 | Ambiguous network/email; clarification | What evidence would resolve the ambiguity? |
| INC-LAB-008 | P2 despite instructions to set P5 | What changes when an LLM reads ticket text? |
| INC-LAB-010 | Missing impact; no priority | Why can't urgency alone determine priority? |

Use **Try your own scenario** for a VPN incident with impact 3 and urgency 3; expect P5 and a preview-only result. Set impact to Unknown; expect clarification and no priority. Add email to create routing ambiguity. Download a result JSON to use as demo evidence.

## Step 7 — Make your first small development change

After the baseline demo, create a separate copy or commit the baseline in your own repository. Add a new route and matching synthetic knowledge article, for example a business application. Add a fixture and an independently written expectation, then add a test describing its behavior. Run all checks before refreshing the snapshot:

```bash
python3 scripts/build_snapshot.py
```

Editing configuration affects subsequent runs. Existing proposals are blocked on approval if their input/policy/knowledge has changed. Rerun triage. The UI should explain the new matched evidence.

## Step 8 — Capture learning and customer evidence

Record the engine result, reviewer decision, and the audit. Write a short explanation of the value hypothesis, the failure cases, and which controls require ServiceNow enforcement later. Use `docs/LEARNING_LOG.md` as your working template.

Success for our first session means you can run the commands, explain one complete result, demonstrate an approved local update, and show one blocked case.

## Troubleshooting

- Module not found: run from the directory containing `lab`, rather than its parent or the `lab` directory itself.
- Address already in use: `python3 -m lab serve --port 8766`, then use the printed URL.
- UI cannot load records: start the Python server and open its printed `127.0.0.1` URL. Opening `visual/index.html` as a file does not start Python.
- Only snapshot interactions work: `offline-snapshot.html` is intentionally precomputed. Use the server for custom scenarios and approvals.
- Stale proposal: select the incident and rerun triage before reviewing it.
- Reviewer required: enter a short name; this is demo attribution, not account authentication.
- Previously approved changes still present: use a new `--db` filename to start a clean demo without deleting your previous evidence.
