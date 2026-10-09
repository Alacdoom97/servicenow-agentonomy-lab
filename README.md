# ServiceNow Agentonomy Lab

**Project 00A: Offline foundation. Project 01: Incident triage baseline.**

You are waitlisted for a replacement Personal Developer Instance (PDI). AI Agent Studio access is unknown. This version lets us learn, build, test, and demonstrate a bounded workflow immediately, then compare it with a live ServiceNow implementation later.

This is a Python development project with a local visual interface. It uses deterministic rules, synthetic tickets, and a SQLite mock adapter. It does not use an LLM, contact ServiceNow, or execute AI Agent Studio agents. “Agentonomy” is our learning label for autonomy, tools, policy gates, evidence, and human oversight.

## Start here

1. Extract `servicenow-agentonomy-lab.zip`.
2. Open a terminal inside the extracted `servicenow-agentonomy-lab` directory, the one containing `lab`, `tests`, and this README.
3. Verify Python 3.10 or newer. No third-party dependencies, API keys, package installs, or PDI are required.
4. Run the environment check, tests, evaluation, and server below.

```bash
python3 -m lab doctor
python3 -m unittest discover -s tests -v
python3 -m lab evaluate
python3 -m lab serve
```

On Windows, use `py -3` in place of `python3`. On systems where the interpreter is named `python`, use that command after confirming its version.

5. Open **http://127.0.0.1:8765** in your browser. Keep the terminal running. Ctrl+C stops the server.
6. Follow [the step-by-step guide](docs/GETTING_STARTED.md) and [the demo script](projects/01-incident-triage/DEMO.md).

For a quick view without Python, open `visual/offline-snapshot.html` directly in your browser. It lets you explore ten precomputed results produced by the same Python engine. Custom input and approval require the live local server.

## What works

- Five bounded steps: input validation, classification/routing, priority calculation, synthetic knowledge retrieval, policy gate.
- Network, email, and device routing with matched terms and reasoning.
- Missing information and ambiguous routing produce clarification questions.
- Security signals and P1/P2 cases cannot use the standard approval path.
- Approve/reject workflow with named local reviewer, SQLite persistence, revision checking, per-run idempotency, transactional updates, and audit events.
- Only category, assignment group, and work notes change on approval. Revision is internal mock metadata. Priority is a suggestion.
- Custom scenarios are preview-only; result JSON is downloadable.
- CLI doctor, single-case demo, and golden-case evaluation.

## Files

| Path | Purpose |
|---|---|
| `lab/engine.py` | Pure deterministic triage engine |
| `lab/store.py` | SQLite mock incidents, proposals, approval, and audit |
| `lab/server.py` | Loopback HTTP API and local visual UI |
| `lab/__main__.py` | Command-line entry point |
| `config/policy.json` | Lab routing and priority policy |
| `data/incidents.json` | Ten synthetic incidents |
| `data/knowledge.json` | Three synthetic knowledge articles |
| `data/expected.json` | Explicit expected results |
| `visual/index.html` | Local server interface |
| `visual/offline-snapshot.html` | Portable precomputed visual demo |
| `scripts/build_snapshot.py` | Regenerates snapshot and sample outputs |
| `tests/test_lab.py` | Behavioral engine, store, concurrency, and HTTP tests |
| `docs/ARCHITECTURE.md` | Architecture and data contracts |
| `docs/SERVICENOW_MAPPING.md` | Platform mapping and future PDI checks |
| `projects/00A-offline-foundation/PROJECT.md` | Foundation scope and acceptance criteria |
| `projects/01-incident-triage/PROJECT.md` | Triage scope, value hypothesis, and backlog |
| `projects/01-incident-triage/DEMO.md` | Customer-facing demo narrative |
| `evidence/` | Generated evaluation and example outputs |

Runtime databases appear under `runtime/` when the server starts; they are not part of the distribution. Use a separate database for a fresh demo:

```bash
python3 -m lab serve --db runtime/demo-fresh.db --port 8766
```

Open the URL printed by the server. Each new database starts with the synthetic fixtures. Reusing a database preserves your approved changes and audit trail.

## Limits that matter

Rules recognize configured words, not meaning. A sentence such as “VPN works; email does not” can produce ambiguous routing. Negation, multilingual descriptions, synonyms, customer-specific service dependencies, and contextual diagnosis are not implemented. No confidence probability is invented.

The fixed tool sequence demonstrates workflow boundaries, evidence, escalation, and human approval. It is not dynamic LLM planning. Ticket instructions cannot execute code or override priority, because the engine does not interpret them as instructions; this does not establish prompt-injection resistance for a future LLM implementation.

The local server has no user authentication. Reviewer names are self-declared. Its audit is an ordinary database history, not tamper-proof evidence. It is for a single learner on loopback, using synthetic data. Reference groups, categories, matrix, and knowledge are lab-specific assumptions. Security detection is keyword-based and incomplete. There are no automatic remediation or resolution actions.

Ten passing teaching scenarios demonstrate these specified behaviors. They do not establish production accuracy, reduced MTTR, or customer ROI. The project guide includes a plan to measure those later.
