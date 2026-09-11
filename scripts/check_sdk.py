"""Construct the real SDK tools/model/AgentCore entrypoint, without calling AWS."""
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import os
os.environ['AWS_EC2_METADATA_DISABLED']='true'
from strands import Agent
from strands.models import BedrockModel
from decisionpilot.catalog import inventory
from decisionpilot.tools import build_tools
from decisionpilot.agent import SYSTEM_PROMPT
from agentcore_main import invoke
trace=[]
tools=build_tools(inventory(),180,'morning',trace)
model=BedrockModel(model_id='amazon.nova-lite-v1:0',region_name='us-east-1')
agent=Agent(model=model,system_prompt=SYSTEM_PROMPT,tools=tools,callback_handler=None)
assert callable(agent)
try:
    invoke({'action':'approve'})
except ValueError:
    pass
else:
    raise AssertionError('AgentCore must not expose approval')
print('PASS: installed SDK constructs Agent and two read-only tools; AgentCore rejects approval payload.')
print('This is NOT a live model invocation. Run bedrock_smoke.py after AWS authorization.')
