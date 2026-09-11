"""No-cloud demonstration; writes an optional synthetic audit export."""
import argparse
import json
from pathlib import Path
import secrets
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from decisionpilot import state
from decisionpilot.agent import run_task

parser=argparse.ArgumentParser()
parser.add_argument('--output', type=Path)
a=parser.parse_args()
owner=secrets.token_hex(32)
tid=state.create_task('Schedule my annual car service under $180, mornings preferred.',owner)
run_task(tid,owner)
try:
    state.execute(tid,owner)
    raise AssertionError('Unsafe booking before approval')
except ValueError:
    print('PASS: execution blocked before human approval')
p=state.snapshot(tid,owner)['proposals'][-1]
state.decide(tid,p['id'],owner,True,60)
first=state.execute(tid,owner)
assert first==state.execute(tid,owner)
assert state.verify(tid,owner)
snap=state.snapshot(tid,owner)
print('PASS: approved → executed once → verified → completed')
print('Estimated minutes saved:',snap['metrics']['human_minutes_saved'],'(35-minute assumed baseline; 60-second test fixture)')
if a.output:
    a.output.parent.mkdir(parents=True,exist_ok=True)
    snap['evidence_note']='Offline deterministic test fixture. Human attention was supplied as 60 seconds, not measured. All providers and receipts are synthetic.'
    a.output.write_text(json.dumps(snap,indent=2)+'\n')
