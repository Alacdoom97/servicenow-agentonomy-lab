"""Behavioral specification for service-specific ambiguity questions."""
import unittest
from pathlib import Path
import tempfile
from unittest.mock import patch
from lab.engine import triage
from lab.store import Store, Conflict


class ClarificationTests(unittest.TestCase):
    def incident(self, description):
        return {"number": "CLARIFICATION-PREVIEW", "short_description": description,
                "impact": 2, "urgency": 2}

    def test_vpn_outlook_asks_about_dependency_without_guessing_route(self):
        result = triage(self.incident("VPN and Outlook unavailable"))
        self.assertEqual(result["questions"], [
            "Are VPN and Outlook failing independently, or does Outlook fail only when you use VPN?"
        ])
        self.assertEqual(result["assignment_group"], "Service Desk")
        self.assertEqual(result["status"], "needs_information")
        self.assertEqual(result["priority"], 3)
        self.assertEqual(result["knowledge"], [])

    def test_other_ambiguity_names_matched_groups_without_inventing_vpn(self):
        result = triage(self.incident("WiFi and email unavailable"))
        self.assertEqual(result["questions"], [
            "The description matches Network Support and Messaging Support. "
            "Which service fails first, and what exact error does each show?"
        ])
        self.assertEqual(result["assignment_group"], "Service Desk")

    def test_unrecognized_issue_keeps_general_intake_question(self):
        result = triage(self.incident("Something is broken"))
        self.assertEqual(result["questions"], [
            "Which service or device is affected, and what exact error do you see?"
        ])

    def test_security_still_takes_precedence_over_vpn_outlook_question(self):
        result = triage(self.incident("VPN and Outlook unavailable after phishing"))
        self.assertEqual(result["assignment_group"], "Security Response")
        self.assertEqual(result["status"], "escalation_required")
        self.assertEqual(result["questions"], [])

    def test_engine_upgrade_refreshes_cached_proposal(self):
        with tempfile.TemporaryDirectory() as temporary:
            store = Store(Path(temporary) / "lab.db")
            with patch('lab.engine.ENGINE_VERSION', 'triage-1'):
                old = store.run('INC-LAB-007')
            new = store.run('INC-LAB-007')
            self.assertNotEqual(new['run_id'], old['run_id'])
            self.assertEqual(new['engine_version'], 'triage-2')
            self.assertEqual(new['questions'], [
                "Are VPN and Outlook failing independently, or does Outlook fail only when you use VPN?"
            ])
            self.assertEqual(store.run('INC-LAB-007'), new)

    def test_engine_upgrade_blocks_old_approval(self):
        with tempfile.TemporaryDirectory() as temporary:
            store = Store(Path(temporary) / "lab.db")
            with patch('lab.engine.ENGINE_VERSION', 'triage-1'):
                old = store.run('INC-LAB-001')
            with self.assertRaises(Conflict):
                store.decide(old['run_id'], 'approve', 'Learner')
            self.assertEqual(store.get('INC-LAB-001')['revision'], 0)


if __name__ == "__main__":
    unittest.main()
