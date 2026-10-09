import copy
import json
import sqlite3
from pathlib import Path
import tempfile
import threading
import unittest
import urllib.request
import urllib.error
from lab.engine import load, triage
from lab.store import Store, Conflict
from lab.server import make_server
from lab.__main__ import evaluate

class EngineTests(unittest.TestCase):
    def incident(self, index=0): return copy.deepcopy(load("data/incidents.json")[index])
    def test_golden_scenarios(self):
        report=evaluate()
        self.assertEqual(report["passed"],report["total"],report)
    def test_all_nine_priority_combinations(self):
        matrix={(1,1):1,(1,2):2,(1,3):3,(2,1):2,(2,2):3,(2,3):4,(3,1):3,(3,2):4,(3,3):5}
        for (impact,urgency),expected in matrix.items():
            with self.subTest(impact=impact,urgency=urgency):
                i=self.incident();i.update(impact=impact,urgency=urgency)
                self.assertEqual(triage(i)["priority"],expected)
    def test_missing_information_never_invents_priority(self):
        r=triage(self.incident(9));self.assertIsNone(r["priority"]);self.assertTrue(r["questions"])
    def test_security_takes_precedence_over_email_route(self):
        r=triage(self.incident(5));self.assertEqual(r["category"],"security");self.assertEqual(r["status"],"escalation_required")
    def test_ambiguous_route_is_not_guessed(self):
        r=triage(self.incident(6));self.assertEqual(r["assignment_group"],"Service Desk");self.assertTrue(r["questions"])
    def test_instruction_text_cannot_override_priority(self):
        r=triage(self.incident(7));self.assertEqual(r["priority"],2);self.assertFalse(r["automatic_write"])
    def test_substrings_do_not_route(self):
        i=self.incident();i.update(short_description='Laptop issue',description='The user installed a mailboxed application')
        self.assertEqual(triage(i)["category"],"hardware")
    def test_invalid_input_rejected(self):
        for bad in (True,0,4,'1',[],1.5):
            with self.subTest(bad=bad):
                i=self.incident();i['impact']=bad
                with self.assertRaises(ValueError):triage(i)
    def test_determinism_and_no_input_mutation(self):
        i=self.incident();before=copy.deepcopy(i)
        self.assertEqual(triage(i),triage(i));self.assertEqual(i,before)
        self.assertEqual(len(triage(i)['trace']),5)
    def test_policy_change_invalidates_run_identity(self):
        p=load('config/policy.json');r=triage(self.incident(),p);p['version']='v2'
        self.assertNotEqual(r['run_id'],triage(self.incident(),p)['run_id'])

class StoreTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.path=Path(self.tmp.name)/'lab.db';self.store=Store(self.path)
    def tearDown(self): self.tmp.cleanup()
    def test_connection_commits_and_closes_on_success(self):
        with self.store.connect() as db:
            db.execute("UPDATE incidents SET revision=7 WHERE number='INC-LAB-001'")
        with self.assertRaises(sqlite3.ProgrammingError):
            db.execute('SELECT 1')
        with self.store.connect() as fresh:
            revision=fresh.execute("SELECT revision FROM incidents WHERE number='INC-LAB-001'").fetchone()[0]
        self.assertEqual(revision,7)
    def test_connection_rolls_back_and_closes_on_exception(self):
        with self.assertRaisesRegex(RuntimeError,'abort transaction'):
            with self.store.connect() as db:
                db.execute("UPDATE incidents SET revision=7 WHERE number='INC-LAB-001'")
                raise RuntimeError('abort transaction')
        with self.assertRaises(sqlite3.ProgrammingError):
            db.execute('SELECT 1')
        with self.store.connect() as fresh:
            revision=fresh.execute("SELECT revision FROM incidents WHERE number='INC-LAB-001'").fetchone()[0]
        self.assertEqual(revision,0)
    def test_store_operations_leave_no_open_connections(self):
        from unittest.mock import patch
        original_connect=sqlite3.connect
        connections=[]
        def track_connection(*args,**kwargs):
            db=original_connect(*args,**kwargs)
            connections.append(db)
            return db
        try:
            with patch('lab.store.sqlite3.connect',side_effect=track_connection):
                other=Store(self.path)
                other.incidents();other.get('INC-LAB-001')
                r=other.run('INC-LAB-001')
                other.run('INC-LAB-001')
                other.decide(r['run_id'],'approve','A')
                other.decide(r['run_id'],'approve','A')
                other.audit()
                with self.assertRaises(KeyError):other.run('MISSING')
                blocked=other.run('INC-LAB-004')
                with self.assertRaises(Conflict):other.decide(blocked['run_id'],'approve','A')
            # Strong references prevent garbage collection from hiding leaked handles.
            self.assertGreater(len(connections),0)
            for db in connections:
                with self.assertRaises(sqlite3.ProgrammingError):db.execute('SELECT 1')
        finally:
            for db in connections:db.close()
    def test_no_write_before_approval(self):
        before=self.store.get('INC-LAB-001');self.store.run(before['number'])
        self.assertEqual(before,self.store.get(before['number']))
    def test_approval_allowlist_and_audit(self):
        before=self.store.get('INC-LAB-001');r=self.store.run(before['number']);self.store.decide(r['run_id'],'approve','Learner')
        after=self.store.get(before['number']);changed={k for k in set(before)|set(after) if before.get(k)!=after.get(k)}
        self.assertEqual(changed,{'category','assignment_group','work_notes','revision'})
        self.assertEqual([e['event'] for e in self.store.audit()],['triage_proposed','review_approve'])
    def test_repeated_run_and_approval_are_idempotent(self):
        r=self.store.run('INC-LAB-001');self.assertEqual(r,self.store.run('INC-LAB-001'))
        self.store.decide(r['run_id'],'approve','A');self.assertTrue(self.store.decide(r['run_id'],'approve','B')['idempotent'])
        self.assertEqual(self.store.get('INC-LAB-001')['revision'],1);self.assertEqual(len(self.store.audit()),2)
    def test_rejection_does_not_change_record(self):
        before=self.store.get('INC-LAB-001');r=self.store.run(before['number']);self.store.decide(r['run_id'],'reject','A')
        self.assertEqual(before,self.store.get(before['number']))
        with self.assertRaises(Conflict):self.store.decide(r['run_id'],'approve','A')
    def test_escalation_and_clarification_cannot_be_approved(self):
        for number in ('INC-LAB-004','INC-LAB-005','INC-LAB-006','INC-LAB-007','INC-LAB-008','INC-LAB-010'):
            r=self.store.run(number)
            with self.subTest(number=number),self.assertRaises(Conflict):self.store.decide(r['run_id'],'approve','A')
    def test_stale_proposal_cannot_overwrite_record(self):
        r=self.store.run('INC-LAB-001')
        with self.store.connect() as db:
            record=self.store.get('INC-LAB-001');record['revision']=1
            db.execute('UPDATE incidents SET revision=1,body=? WHERE number=?',(json.dumps(record),record['number']))
        with self.assertRaises(Conflict):self.store.decide(r['run_id'],'approve','A')
        self.assertNotEqual(r['run_id'],self.store.run('INC-LAB-001')['run_id'])
    def test_restart_preserves_decision_and_record(self):
        r=self.store.run('INC-LAB-001');self.store.decide(r['run_id'],'approve','A');other=Store(self.path)
        self.assertEqual(other.get('INC-LAB-001')['revision'],1)
        self.assertTrue(other.decide(r['run_id'],'approve','A')['idempotent'])
    def test_missing_reviewer_blocked(self):
        r=self.store.run('INC-LAB-001')
        with self.assertRaises(ValueError):self.store.decide(r['run_id'],'approve','')
    def test_changed_policy_blocks_old_approval(self):
        from unittest.mock import patch
        r=self.store.run('INC-LAB-001')
        changed=load('config/policy.json');changed['version']='changed'
        def updated_load(name):
            return changed if name=='config/policy.json' else load(name)
        with patch('lab.engine.load',side_effect=updated_load):
            with self.assertRaises(Conflict):self.store.decide(r['run_id'],'approve','A')
        self.assertEqual(self.store.get('INC-LAB-001')['revision'],0)
    def test_concurrent_approvals_write_once(self):
        from concurrent.futures import ThreadPoolExecutor
        r=self.store.run('INC-LAB-001')
        with ThreadPoolExecutor(max_workers=2) as pool:
            results=list(pool.map(lambda _:self.store.decide(r['run_id'],'approve','A'),range(2)))
        self.assertEqual(sum(not x['idempotent'] for x in results),1)
        self.assertEqual(self.store.get('INC-LAB-001')['revision'],1)

class HttpTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.server=make_server(Store(Path(self.tmp.name)/'db'),0)
        self.thread=threading.Thread(target=self.server.serve_forever,daemon=True);self.thread.start()
        self.base=f'http://127.0.0.1:{self.server.server_port}'
    def tearDown(self):self.server.shutdown();self.server.server_close();self.thread.join();self.tmp.cleanup()
    def request(self,path,body=None,origin=None):
        headers={'Content-Type':'application/json'}
        if origin:headers['Origin']=origin
        req=urllib.request.Request(self.base+path,data=json.dumps(body).encode() if body is not None else None,headers=headers)
        try:
            return urllib.request.urlopen(req,timeout=3)
        except urllib.error.HTTPError as error:
            # Error responses own file-like resources too; status remains readable after close.
            error.close()
            raise
    def test_ui_and_health(self):
        with self.request('/') as r:self.assertIn('Incident triage',r.read().decode())
        with self.request('/api/health') as r:self.assertEqual(json.load(r)['mode'],'offline')
    def test_end_to_end_approval(self):
        with self.request('/api/triage',{'number':'INC-LAB-001'}) as r:proposal=json.load(r)
        with self.request('/api/decision',{'run_id':proposal['run_id'],'decision':'approve','reviewer':'Demo'}) as r:self.assertEqual(json.load(r)['decision'],'approve')
        with self.request('/api/incidents') as r:self.assertEqual(json.load(r)[0]['assignment_group'],'Network Support')
    def test_custom_preview_and_bad_input(self):
        with self.request('/api/preview',{'number':'CUSTOM','short_description':'VPN outage','impact':1,'urgency':1}) as r:self.assertEqual(json.load(r)['status'],'escalation_required')
        with self.assertRaises(urllib.error.HTTPError) as e:self.request('/api/preview',{'number':'CUSTOM'})
        self.assertEqual(e.exception.code,400)
    def test_cross_origin_write_blocked(self):
        with self.assertRaises(urllib.error.HTTPError) as e:self.request('/api/triage',{'number':'INC-LAB-001'},'https://example.com')
        self.assertEqual(e.exception.code,403)
    def test_oversized_input_blocked(self):
        with self.assertRaises(urllib.error.HTTPError) as e:self.request('/api/preview',{'number':'CUSTOM','short_description':'X','description':'x'*17000})
        self.assertEqual(e.exception.code,400)
    def test_bad_record_identifier_is_a_client_error(self):
        with self.assertRaises(urllib.error.HTTPError) as e:self.request('/api/triage',{'number':[]})
        self.assertEqual(e.exception.code,400)

if __name__=='__main__':unittest.main()
