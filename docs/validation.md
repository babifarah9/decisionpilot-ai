# Validation report — September 11, 2026

## Result

**Working local deterministic MVP; cloud and publication gates remain blocked.** This report does not certify the project as ready to submit.

| Check | Result |
|---|---|
| Starter inspection | Completed; source, manifest, tests and existing assets inspected |
| Python compilation | Passed on Python 3.12 |
| Core lifecycle + HTTP tests | 32 passed |
| Offline safety demonstration | Passed: preapproval blocked; approved execution idempotent; receipt verified |
| JavaScript syntax | Passed `node --check` |
| Secrets scan | Passed heuristic scan; no credential values found |
| Architecture visual inspection | PNG rendered and inspected |
| SDK dependency installation | Blocked by environment network approval cancellation |
| Real SDK construction | Blocked: `ModuleNotFoundError: No module named 'strands'` |
| Live Strands/Bedrock invocation | Not performed; credentials absent and SDK unavailable |
| AgentCore deployment | Not performed; owner AWS authorization required |
| Container build / public deployment | Prepared, not executed |
| Browser visual QA / screenshots | Blocked: cloud browser rejected access to local address |
| Public repository lookup | Confirmed public with push access: `babifarah9/decisionpilot-ai` |
| Public repository publication | Source release prepared for the connected public repository; verify the current commit and Actions results |
| Devpost / Builder publication | Drafts prepared; not published |

## Changes from the supplied starter

- Removed shared cached Agent state; each model-backed planning invocation creates a fresh Agent.
- Removed approval and booking execution from the agent-facing surface entirely.
- Replaced post-mutation task checks with pre-mutation session ownership and proposal binding.
- Added explicit terminal decisions, expiration and content fingerprinting.
- Replaced duplicate-prone writes with transactional, uniquely keyed simulated receipts.
- Made verification compare actual stored receipt fields and withhold completion on mismatch.
- Added restart handling for interrupted planning; preserved pending/approved workflows for human recovery.
- Added bounded cloud runs, model calls, request size and planning concurrency.
- Replaced the package-dependent Streamlit UI with a dependency-free HTTP/HTML UI.
- Replaced fixed eight-second attention with browser active-time accounting and disclosed assumptions.
- Removed stale compiled files from the distributable and excluded runtime databases/secrets.
- Added setup, deployment, CI, architecture, submission drafts and opt-in AWS verification scripts.

## Test coverage

Lifecycle tests cover successful completion, execution without approval, rejection, ownership, cross-task proposals, approval replay, duplicate and concurrent execution, concurrent decisions, expiration before/after approval, tampering, missing receipt, premature verification, process-restart persistence, no-match, strict budget/daypart filtering, invalid values, missing approval tools, invalid model selection, model failure without offline substitution, cloud limits, explicit boolean approval, invalid attention, interrupted planning and proposal replacement.

HTTP tests cover the full application path, session isolation, CSRF, foreign origin rejection, static assets/security headers and invalid payloads. These run a real local HTTP server in-process; they are not browser rendering tests. Core tests use deterministic inventory. Mocked model failures test the controller's error path, not the SDK implementation.

## Limitations requiring disclosure

Provider inventory and receipt creation are simulated. No real appointment search, payment, email or calendar action occurs. Local SQLite is not a distributed store, and its audit is not tamper-proof. Anonymous cookie identity is for synthetic demo sessions only. The attention baseline is assumed, and active browser time is an imperfect proxy. Cloud compatibility and visual polish must be validated with the scripts/shot list after access is available.

## Reproduction commands

```bash
python -m unittest discover -s tests -v
python scripts/safety_demo.py
python scripts/scan_secrets.py
python -m compileall -q decisionpilot agentcore_main.py
node --check decisionpilot/web/app.js
```

After dependency access and AWS owner authorization:

```bash
python -m pip install '.[aws]'
python -m pip check
python scripts/check_sdk.py
python scripts/bedrock_smoke.py --allow-aws-call
```

Record actual cloud outputs, installed versions, successful UI checks and public URLs here before changing the release decision.
