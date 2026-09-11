"""Opt-in paid Bedrock test. Never run without the AWS account owner's authorization."""
import argparse
import json
from pathlib import Path
import secrets
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
p=argparse.ArgumentParser()
p.add_argument('--allow-aws-call',action='store_true',help='Authorize metered Bedrock model calls in your configured account')
p.add_argument('--output',type=Path,default=Path('.decisionpilot/bedrock-evidence.json'))
a=p.parse_args()
if not a.allow_aws_call:
    p.error('AWS authorization required. Review cost and credentials, then use --allow-aws-call.')
import boto3
from decisionpilot.agent import run_task
from decisionpilot import state
session=boto3.Session()
if not session.get_credentials():
    raise SystemExit('No AWS credentials. Sign in locally with AWS IAM Identity Center; never paste secrets into chat.')
owner=secrets.token_hex(32)
tid=state.create_task('Schedule my annual car service under $180. I prefer a morning appointment and the best balance of rating and price.',owner,mode='bedrock')
run_task(tid,owner)
s=state.snapshot(tid,owner)
assert s['status']=='WAITING_FOR_HUMAN' and s['booking'] is None
assert s['proposals'][-1]['candidate']['id']=='central-0830'
a.output.parent.mkdir(parents=True,exist_ok=True)
a.output.write_text(json.dumps(s,indent=2)+'\n')
print('PASS: live Strands/Bedrock planning reached Human Decision Gate; no booking was executed.')
print('Evidence saved locally. Complete the human click path in the UI separately.')
