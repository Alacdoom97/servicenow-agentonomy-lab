"""Regenerate the portable visual demo using Python engine outputs."""
from pathlib import Path
import json
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from lab.engine import load,triage
from lab.__main__ import evaluate
payload={'incidents':load('data/incidents.json'),'results':[triage(i) for i in load('data/incidents.json')]}
# Escape script-breaking characters if future fixtures contain arbitrary ticket text.
encoded=json.dumps(payload,ensure_ascii=False).replace('<','\\u003c').replace('>','\\u003e').replace('&','\\u0026').replace('\u2028','\\u2028').replace('\u2029','\\u2029')
html=(ROOT/'visual/index.html').read_text()
html=html.replace('<script>','<script>window.LAB_SNAPSHOT='+encoded+';</script>\n<script>',1)
(ROOT/'visual/offline-snapshot.html').write_text(html)
(ROOT/'evidence').mkdir(exist_ok=True)
(ROOT/'evidence/evaluation.json').write_text(json.dumps(evaluate(),indent=2)+'\n')
(ROOT/'evidence/example-triage.json').write_text(json.dumps(payload['results'][0],indent=2)+'\n')
print('Generated visual snapshot, evaluation, and example output.')
