"""Deterministic triage baseline. Ticket text is data, never executable instructions."""
import hashlib
import json
import re
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
ENGINE_VERSION = "triage-2"

def load(name):
    return json.loads((ROOT / name).read_text(encoding="utf-8"))

def validate(incident):
    if not isinstance(incident, dict):
        raise ValueError("Incident must be a JSON object")
    for field in ("number", "short_description"):
        if not isinstance(incident.get(field), str) or not incident[field].strip():
            raise ValueError(f"{field} must be a non-empty string")
        if len(incident[field]) > (80 if field == "number" else 160):
            raise ValueError(f"{field} is too long")
    if not isinstance(incident.get("description", ""), str) or len(incident.get("description", "")) > 8000:
        raise ValueError("description must be text of at most 8000 characters")
    for field in ("impact", "urgency"):
        value = incident.get(field)
        if value is not None and (type(value) is not int or value not in (1, 2, 3)):
            raise ValueError(f"{field} must be an integer 1, 2, or 3, or null")

def matches(text, keyword):
    return re.search(r"(?<!\w)" + re.escape(keyword) + r"(?!\w)", text) is not None

def triage(incident, policy=None, knowledge=None):
    validate(incident)
    policy = policy if policy is not None else load("config/policy.json")
    knowledge = knowledge if knowledge is not None else load("data/knowledge.json")
    text = (incident["short_description"] + " " + incident.get("description", "")).casefold()
    trace = [{"step": 1, "tool": "validate_incident", "result": "Valid input; ticket text treated as untrusted data"}]
    security = [k for k in policy["security_keywords"] if matches(text, k)]
    candidates = [(r, [k for k in r["keywords"] if matches(text, k)]) for r in policy["routes"]]
    candidates = [(r, words) for r, words in candidates if words]
    questions = []
    if security:
        category, group, evidence = "security", "Security Response", security
        explanation = "Security signal detected; a specialist must assess and route the incident."
    elif len(candidates) == 1:
        route, evidence = candidates[0]
        category, group = route["category"], route["group"]
        explanation = f"One routing rule matched: {', '.join(evidence)}."
    else:
        category, group = "inquiry", "Service Desk"
        evidence = [word for _, words in candidates for word in words]
        explanation = "Multiple routing rules matched." if candidates else "No routing rule matched."
        if len(candidates) == 2 and {"vpn", "outlook"}.issubset(evidence):
            questions.append("Are VPN and Outlook failing independently, or does Outlook fail only when you use VPN?")
        elif len(candidates) > 1:
            groups = list(dict.fromkeys(route["group"] for route, _ in candidates))
            group_names = " and ".join(groups) if len(groups) <= 2 else ", ".join(groups[:-1]) + ", and " + groups[-1]
            questions.append(f"The description matches {group_names}. Which service fails first, and what exact error does each show?")
        else:
            questions.append("Which service or device is affected, and what exact error do you see?")
    trace.append({"step": 2, "tool": "classify_and_route", "result": explanation})
    for field in ("impact", "urgency"):
        if incident.get(field) is None:
            questions.append("How many people or business services are affected? Supply impact 1–3." if field == "impact" else "How long can resolution wait, and is there a workaround? Supply urgency 1–3.")
    priority = policy["priority_matrix"].get(f'{incident.get("impact")},{incident.get("urgency")}')
    trace.append({"step": 3, "tool": "calculate_priority", "result": f"Lab matrix gives P{priority}" if priority else "Impact or urgency missing; no priority inferred"})
    articles = [k for k in knowledge if k["category"] == category]
    trace.append({"step": 4, "tool": "retrieve_knowledge", "result": [k["number"] for k in articles]})
    status = "escalation_required" if security or priority in (1, 2) else "needs_information" if questions else "awaiting_approval"
    trace.append({"step": 5, "tool": "apply_policy_gate", "result": status})
    proposal = {"category": category, "assignment_group": group,
                "work_notes": f"Offline lab triage: {explanation} Suggested priority: {priority if priority else 'unknown'}. Knowledge: {', '.join(k['number'] for k in articles) or 'none'}."}
    source = json.dumps({"incident": incident, "policy": policy, "knowledge": knowledge,
                         "engine_version": ENGINE_VERSION}, sort_keys=True)
    return {"run_id": hashlib.sha256(source.encode()).hexdigest()[:24], "number": incident["number"],
            "source_revision": incident.get("revision", 0), "policy_version": policy["version"],
            "engine_version": ENGINE_VERSION,
            "status": status, "category": category, "assignment_group": group, "priority": priority,
            "evidence": evidence, "explanation": explanation, "questions": questions,
            "knowledge": articles, "proposal": proposal, "trace": trace,
            "execution_mode": "offline_deterministic", "automatic_write": False}
