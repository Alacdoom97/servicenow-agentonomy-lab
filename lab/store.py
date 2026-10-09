"""SQLite mock record adapter: transactional approval, revision checks, audit, idempotency."""
import json
import sqlite3
from contextlib import contextmanager
from .engine import load, triage

class Conflict(ValueError):
    pass

class Store:
    def __init__(self, path):
        self.path = str(path)
        with self.connect() as db:
            db.executescript("""
            CREATE TABLE IF NOT EXISTS incidents (number TEXT PRIMARY KEY, body TEXT NOT NULL, revision INTEGER NOT NULL);
            CREATE TABLE IF NOT EXISTS runs (run_id TEXT PRIMARY KEY, number TEXT NOT NULL, result TEXT NOT NULL, decision TEXT);
            CREATE TABLE IF NOT EXISTS audit (id INTEGER PRIMARY KEY AUTOINCREMENT, created_at TEXT DEFAULT CURRENT_TIMESTAMP, event TEXT NOT NULL, body TEXT NOT NULL);
            """)
            for incident in load("data/incidents.json"):
                db.execute("INSERT OR IGNORE INTO incidents VALUES (?,?,?)", (incident["number"], json.dumps(incident), 0))

    @contextmanager
    def connect(self):
        """Commit or roll back the transaction, then always release its file handle."""
        db = sqlite3.connect(self.path, timeout=5)
        try:
            # SQLite's own context manager handles transactions, not connection lifetime.
            with db:
                yield db
        finally:
            db.close()

    def incidents(self):
        with self.connect() as db:
            return [json.loads(row[0]) for row in db.execute("SELECT body FROM incidents ORDER BY number")]

    def get(self, number):
        with self.connect() as db:
            row = db.execute("SELECT body FROM incidents WHERE number=?", (number,)).fetchone()
        if not row:
            raise KeyError("Incident not found")
        return json.loads(row[0])

    @staticmethod
    def log(db, event, body):
        db.execute("INSERT INTO audit(event,body) VALUES (?,?)", (event, json.dumps(body)))

    def run(self, number):
        if not isinstance(number, str) or not number.strip() or len(number) > 80:
            raise ValueError("number must be a string of 1–80 characters")
        with self.connect() as db:
            db.execute("BEGIN IMMEDIATE")
            row = db.execute("SELECT body FROM incidents WHERE number=?", (number,)).fetchone()
            if not row:
                raise KeyError("Incident not found")
            result = triage(json.loads(row[0]))
            old = db.execute("SELECT result FROM runs WHERE run_id=?", (result["run_id"],)).fetchone()
            if old:
                return json.loads(old[0])
            db.execute("INSERT INTO runs VALUES (?,?,?,NULL)", (result["run_id"], number, json.dumps(result)))
            self.log(db, "triage_proposed", result)
            return result

    def decide(self, run_id, decision, reviewer):
        if not isinstance(run_id, str) or not run_id or len(run_id) > 80:
            raise ValueError("run_id must be a string of 1–80 characters")
        if decision not in ("approve", "reject"):
            raise ValueError("decision must be approve or reject")
        if not isinstance(reviewer, str) or not reviewer.strip() or len(reviewer) > 80:
            raise ValueError("A reviewer name of 1–80 characters is required")
        with self.connect() as db:
            db.execute("BEGIN IMMEDIATE")
            row = db.execute("SELECT number,result,decision FROM runs WHERE run_id=?", (run_id,)).fetchone()
            if not row:
                raise KeyError("Run not found")
            number, raw, previous = row
            result = json.loads(raw)
            if previous:
                if previous != decision:
                    raise Conflict("Run already has a different decision")
                return {"run_id": run_id, "decision": previous, "idempotent": True}
            if decision == "approve" and result["status"] != "awaiting_approval":
                raise Conflict("This run requires clarification or escalation; standard approval is blocked")
            record_raw, revision = db.execute("SELECT body,revision FROM incidents WHERE number=?", (number,)).fetchone()
            if revision != result["source_revision"]:
                raise Conflict("Incident changed since triage; run triage again")
            if decision == "approve":
                record = json.loads(record_raw)
                if triage(record)["run_id"] != run_id:
                    raise Conflict("Policy or knowledge changed since triage; run triage again")
                # Only these three fields may change; priority, state, impact, urgency cannot be written here.
                for field in ("category", "assignment_group"):
                    record[field] = result["proposal"][field]
                record["work_notes"] = (record.get("work_notes", "") + "\n" + result["proposal"]["work_notes"]).strip()
                record["revision"] = revision + 1
                db.execute("UPDATE incidents SET body=?,revision=? WHERE number=?", (json.dumps(record), revision+1, number))
            db.execute("UPDATE runs SET decision=? WHERE run_id=?", (decision, run_id))
            self.log(db, "review_" + decision, {"run_id": run_id, "reviewer": reviewer.strip(), "number": number})
            return {"run_id": run_id, "decision": decision, "idempotent": False}

    def audit(self):
        with self.connect() as db:
            return [{"id": r[0], "created_at": r[1], "event": r[2], "body": json.loads(r[3])} for r in db.execute("SELECT id,created_at,event,body FROM audit ORDER BY id")]
