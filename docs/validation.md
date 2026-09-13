# Validation report — September 13, 2026

## Result

**Working deterministic MVP and verified live Strands/Bedrock planning; public hosting and browser acceptance remain pending.** This report does not certify the project as ready to submit.

| Check | Result |
|---|---|
| Starter inspection | Completed; source, manifest, tests and existing assets inspected |
| Python compilation | Passed on Python 3.12 |
| Core lifecycle + HTTP tests | 32 passed locally and in GitHub CI on Python 3.12 and 3.13 |
| Offline safety demonstration | Passed: preapproval blocked; approved execution idempotent; receipt verified |
| JavaScript syntax | Passed `node --check` |
| Secrets scan | Passed heuristic scan; no credential values found |
| Architecture visual inspection | PNG rendered and inspected |
| SDK dependency installation | Passed on GitHub CI; pip check also passed |
| Real SDK construction | Passed on GitHub CI; two read-only tools and AgentCore rejection of approval payload verified |
| Live Strands/Bedrock invocation | Passed September 13: Nova Lite planning reached the human gate; no booking executed |
| AgentCore deployment | Not performed; owner AWS authorization required |
| Container build / public deployment | Prepared, not executed |
| Browser visual QA / screenshots | Blocked: cloud browser rejected access to local address |
| Public repository lookup | Confirmed public with push access: `babifarah9/decisionpilot-ai` |
| Public repository publication | 41-file source release published; GitHub detects MIT license; all three initial CI jobs passed |
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

Provider inventory and receipt creation are simulated. No real appointment search, payment, email or calendar action occurs. Local SQLite is not a distributed store, and its audit is not tamper-proof. Anonymous cookie identity is for synthetic demo sessions only. The attention baseline is assumed, and active browser time is an imperfect proxy. Cloud planner compatibility passed; deployed UI behavior and visual polish still need browser validation.

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

## GitHub evidence

[Passing CI run](https://github.com/babifarah9/decisionpilot-ai/actions/runs/34615901169) for source commit `1b67769bfc7de631db53f4c19c57924acb9520f6`. [Live AWS workflow passed](https://github.com/babifarah9/decisionpilot-ai/actions/runs/34779404240); OIDC authentication, SDK installation, model-backed planning and evidence upload all succeeded.

## Prepared deployment validation

Public CloudFormation template passed `cfn-lint` for us-east-1. Launcher Python compilation, embedded bootstrap/configuration shell syntax, exact HTTPS-origin handling and rejection of malformed host URLs passed. All 32 existing tests passed again. These checks do not establish that AWS provisioning or browser acceptance has succeeded.
