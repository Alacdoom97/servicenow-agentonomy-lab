import argparse
import json
import platform
import sys
from pathlib import Path
from .engine import ROOT, load, triage
from .store import Store

def evaluate():
    expected = {item["number"]:item for item in load("data/expected.json")}
    cases=[]
    for incident in load("data/incidents.json"):
        result=triage(incident)
        target=expected[incident["number"]]
        fields=("category", "assignment_group", "priority", "status")
        cases.append({"number":incident["number"], "passed":all(result[k]==target[k] for k in fields), "actual":{k:result[k] for k in fields}, "expected":{k:target[k] for k in fields}})
    return {"dataset":"10 synthetic teaching cases; not a production accuracy estimate", "passed":sum(c["passed"] for c in cases), "total":len(cases), "cases":cases}

def main():
    parser=argparse.ArgumentParser(description="ServiceNow Agentonomy Lab — offline")
    sub=parser.add_subparsers(dest="command",required=True)
    sub.add_parser("doctor")
    demo=sub.add_parser("demo"); demo.add_argument("--number", default="INC-LAB-001")
    sub.add_parser("evaluate")
    serve=sub.add_parser("serve"); serve.add_argument("--port",type=int,default=8765); serve.add_argument("--db",default=str(ROOT/"runtime/lab.db"))
    args=parser.parse_args()
    if args.command=="doctor":
        if sys.version_info < (3,10): parser.error("Python 3.10 or newer required")
        checks={"python":platform.python_version(),"mode":"offline", "pdi":"unavailable / waitlist (user reported)","ai_agent_studio":"unknown; no access assumed", "external_dependencies":0, "live_servicenow_calls":False, "fixtures":len(load('data/incidents.json')), "policy":load('config/policy.json')['version']}
        print(json.dumps(checks,indent=2))
    elif args.command=="demo":
        incident=next((i for i in load("data/incidents.json") if i["number"]==args.number), None)
        if incident is None: parser.error("Unknown incident number")
        print(json.dumps(triage(incident),indent=2))
    elif args.command=="evaluate":
        report=evaluate();print(json.dumps(report,indent=2));return 0 if report['passed']==report['total'] else 1
    elif args.command=="serve":
        from .server import make_server
        path=Path(args.db);path.parent.mkdir(parents=True,exist_ok=True)
        server=make_server(Store(path),args.port)
        print(f"Open http://127.0.0.1:{server.server_port} — Ctrl+C stops the demo",flush=True)
        try: server.serve_forever()
        except KeyboardInterrupt: pass
        finally:server.server_close()
    return 0
if __name__=="__main__": raise SystemExit(main())
