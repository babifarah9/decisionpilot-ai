# Setup and deployment

Status: **live Strands/Bedrock planning verified; EC2/CloudFront public demo deployed; AgentCore not deployed**. [Passing live run](https://github.com/babifarah9/decisionpilot-ai/actions/runs/34779404240). Start with the [reviewed CloudShell public-demo guide](public-demo-next-step.md).

## 1. Local test build

Use Python 3.12 or newer (below 3.15). From the repository root:

```bash
python -m unittest discover -s tests -v
python -m decisionpilot.server
```

Open `http://localhost:8080`. This runs the deterministic sandbox without external dependencies. The database is `.decisionpilot/workflows-v2.db`. Keep it on persistent storage. The old starter database is not migrated.

Set variables in the shell; `.env.example` is a reference and is not automatically loaded. Restart the server after environment changes. `HOST=127.0.0.1` is the default for local use; container hosting explicitly sets `HOST=0.0.0.0` behind a proxy.

## 2. GitHub source

Public source: https://github.com/babifarah9/decisionpilot-ai

The repository includes source, MIT license, architecture and submission drafts. Review the Actions tab for safety tests and the SDK-install job. After making changes, scan source before committing; do not force-push. Check README rendering, architecture and license visibility in a signed-out browser before submitting the URL.

## 3. AWS credentials and Bedrock — owner authorization required

The $50 credits were reported available by the owner; redemption, remaining balance and expiry were not inspected. In your AWS account, verify those values and create billing alerts before authorizing compute/model use. Do not put keys in source or in chat.

1. Sign in using AWS IAM Identity Center/SSO. Install/configure AWS CLI using official AWS instructions, then use `aws configure sso` and `aws sso login --profile decisionpilot`. Set `AWS_PROFILE=decisionpilot` if using that profile.
2. Confirm the intended AWS account with `aws sts get-caller-identity` locally. Do not publish its output.
3. Start with `us-east-1` and `amazon.nova-lite-v1:0`. Confirm the model is available to your account/region. Grant only the model invocation actions in `deploy/bedrock-policy.json`; update its ARN if you change region/model.
4. Install and validate the real SDK:

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install '.[aws]'
python -m pip check
python scripts/check_sdk.py
export AWS_REGION=us-east-1
export DECISIONPILOT_MODEL=amazon.nova-lite-v1:0
python scripts/bedrock_smoke.py --allow-aws-call
```

This opt-in smoke test incurs AWS usage. It makes the real Strands planner search and evaluate, validates the selected candidate, saves the pending proposal, and asserts that no booking exists. It deliberately does not approve itself. Evidence is written to `.decisionpilot/bedrock-evidence.json` (ignored by git).

5. Set `DECISIONPILOT_MODE=bedrock`, start the UI, and click through approval and rejection yourself. Capture the model-backed success, failure handling and pending gate on video. Confirm a fresh browser session cannot read the first session's tasks.
6. After success, record installed versions with `python -m pip freeze > .decisionpilot/validated-versions.txt`. Review and use them to create a release lockfile; don't label untested version ranges “locked.”

If installation fails, resolve package/network access first. `AccessDeniedException` requires account/role/model review; a validation error may mean an unsupported model ID or inference-profile requirement. Use a supported model and grant the corresponding resources deliberately, rather than broadening to administrator privileges. No cloud error is silently replaced with offline success.

Official reference: [Strands Amazon Bedrock provider](https://strandsagents.com/docs/user-guide/concepts/model-providers/amazon-bedrock/).

## 4. Public HTTPS demo on one persistent host

This deployment path supports AWS EC2, or an existing Docker host. It is **not executed or cost-verified** here. Prefer an existing host if available; do not assume free-tier eligibility. Cloud costs include compute, storage, public IPv4, model calls, and potentially logs/egress. A daily run limit is not a billing limit.

After authorizing the deployment and spend:

1. Provision a small Linux EC2 instance in the chosen account/region. Select size after checking current prices; allow 2 GB RAM for comfortable installation. Use encrypted EBS storage. Use Systems Manager for administration where configured; keep SSH closed unless specifically needed.
2. For Bedrock mode attach a least-privilege instance role containing the model policy. For container access to IMDSv2, set an appropriate response hop limit (normally 2 for the bridge) while retaining IMDSv2 required; verify credentials from the container without printing them. Never bake keys into the image.
3. Point a DNS name you control to the host. Allow inbound 80/443 for Caddy; do not expose 8080 directly. Domain acquisition, if needed, is a separate owner decision.
4. Install Docker Engine and Compose from official instructions. Place the repository on the host and run:

```bash
export DEMO_DOMAIN=your-actual-demo-hostname
export DECISIONPILOT_MODE=offline
# After passing Bedrock smoke testing, change the value to bedrock.
docker compose -f deploy/compose.yaml up -d --build
```

The app is accessible at `https://<your actual hostname>`. Caddy obtains a certificate; the app requires that exact origin and sends a Secure, HttpOnly, SameSite cookie. The database persists in `workflow-data` across container restarts. Do not use `docker compose down -v` unless you intentionally want to erase workflow state. The default anonymous identity is suitable only for the synthetic demo; it is not user-account authentication for real paid workflows.

5. Verify `/health`, run the full browser workflow, reject a second workflow, refresh a pending task, inspect mobile layout, and confirm no duplicate booking after refresh/retry. Keep the demo accessible through judging.
6. To stop compute, stop the instance intentionally after judging. Before terminating it, export any required evidence and make a database backup. EBS is durable across restarts, not automatically across instance termination.

A free third-party static host cannot run the Python controller. Do not publish only the HTML and call it a working agent demo.

## 5. Optional Amazon Bedrock AgentCore

**Architecture:** AgentCore runs `agentcore_main.py`, which accepts only planning inputs and returns a recommendation. It never receives the browser ownership token and exposes no approve, reject or execute actions. SQLite remains with the UI/controller on the persistent host. This avoids approval loss when an AgentCore session ends or scales.

The current AWS guide uses the npm AgentCore CLI. After AWS authorization and installing its prerequisites:

```bash
npm install -g @aws/agentcore
agentcore create --name DecisionPilot --framework Strands --protocol HTTP --model-provider Bedrock --memory none
```

In the generated project:

- Replace the generated `app/DecisionPilot/main.py` with this repository's `agentcore_main.py`.
- Copy `decisionpilot/` beside that entrypoint. Retain the generated packaging configuration; include the same bounded AWS dependencies from this repository's `pyproject.toml` in its dependency list.
- Configure the AWS target/account/region and model environment. Review the generated IAM and CDK resources, scoped for the selected model.
- Run `agentcore dev`. Send the JSON shape below to the local `/invocations` endpoint. Planning responses must reference the strongest eligible candidate and never create state or a booking.
- Run `agentcore deploy --dry-run`, review resource creation and expected cost, then obtain owner approval before `agentcore deploy`.
- Use `agentcore status` to capture the actual runtime ARN. Set `DECISIONPILOT_AGENTCORE_ARN` on the UI host and `DECISIONPILOT_MODE=agentcore`. Grant its host role `bedrock-agentcore:InvokeAgentRuntime` scoped to that ARN.
- Test the UI end to end again. The `plan_remote` client uses the AWS SDK `invoke_agent_runtime` operation; record the observed response format. If the deployed runtime wraps responses differently, fix/test parsing before release.

Planning payload (the caller supplies the same trusted fixture inventory that it later validates):

```json
{"objective":"Schedule my annual car service under $180.","budget":180,"daypart":"morning","candidates":[{"id":"central-0830","provider":"AutoCare Central","slot":"2026-09-16 08:30","cost":139,"rating":4.7}]}
```

This manual staging path is prepared, not a tested one-command deployment. Inspect current CLI-generated files instead of assuming a historical configuration schema. Do not submit an AgentCore claim until an actual invocation is verified. Reference: [AWS AgentCore CLI guide](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/runtime-get-started-cli.html).

## Security boundary and remaining production work

The agent is confined by its registered tools, with no shell, arbitrary HTTP, filesystem, approval or execution tools. The controller distrusts model output. The browser approval is a same-origin session action bound to an exact immutable proposal. A compromised trusted server/database or stolen browser session remains outside this demonstration's protection. Before a real garage/payment integration, add authenticated user identity, provider credentials outside the agent, re-quote handling, provider-side idempotency, external receipt lookup, retention controls, operational recovery, and independent security review.
