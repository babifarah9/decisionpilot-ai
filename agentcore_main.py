"""Optional stateless AgentCore planner. No human approval route or workflow database."""
from bedrock_agentcore.runtime import BedrockAgentCoreApp
from decisionpilot.agent import plan_with_strands
from decisionpilot.catalog import rank

app = BedrockAgentCoreApp()


@app.entrypoint
def invoke(payload: dict) -> dict:
    if set(payload) != {'objective', 'candidates', 'budget', 'daypart'}:
        raise ValueError('Only planning payloads are accepted. Approval is outside AgentCore.')
    if not isinstance(payload['objective'], str) or not 10 <= len(payload['objective']) <= 1200:
        raise ValueError('Invalid objective.')
    if not isinstance(payload['candidates'], list) or len(payload['candidates']) > 20:
        raise ValueError('Invalid inventory.')
    rank(payload['candidates'], payload['budget'], payload['daypart'])
    return plan_with_strands(**payload)


if __name__ == '__main__':
    app.run()
