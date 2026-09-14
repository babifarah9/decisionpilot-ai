# Submission checklist

**Release decision: NOT YET SUBMISSION-READY.** The MVP, live SDK/AWS planning and deployment work; owner-reported browser decision tests pass. Video link supplied; public visibility confirmation and final submission remain unfinished.

Official requirements checked September 11, 2026: [rules](https://agentsforhumans.devpost.com/rules) and [overview](https://agentsforhumans.devpost.com/).

| Requirement | Status / evidence |
|---|---|
| Submit by September 14, 2026, 5 PM PDT | Pending; September 15, 00:00 UTC |
| Eligible entrant; truthful residence/domicile | Owner confirmation; Quebec is excluded |
| New project during competition; disclose earlier work | Owner confirms starter provenance |
| Working Strands project | Live Strands/Nova planning passed September 13 |
| Public source repository, README and MIT/Apache license | Source included in this public repository; check Actions |
| Architecture diagram | PNG, SVG and Mermaid ready |
| Description | `submission_draft.md` ready for review |
| Public YouTube/Vimeo video, ≤5 minutes | Edited 2:02 video uploaded by owner: https://youtu.be/txn8iroBFnw; confirm Public visibility |
| AWS Builder ID | Owner supplies |
| Free judging access through October 8 | Public HTTPS demo available; maintain access and credits through judging |
| English materials and rights clearance | Drafts English; owner confirms rights |
| Optional live demo / AgentCore | EC2/Bedrock/CloudFront demo deployed; AgentCore not deployed |
| Optional public Builder article with Agents for Humans title | Draft ready; publication pending |

## Product release gates

- [x] Core and HTTP lifecycle tests pass.
- [x] Agent tool set contains no approval or execution capability.
- [x] Ownership checked before decision mutation.
- [x] Approval/rejection, expiration, replay and concurrent execution tested.
- [x] Persistent state, audit and simulated receipt verification implemented.
- [x] Secrets excluded from release package; heuristic scan passes.
- [x] Architecture distinguishes current code from optional cloud infrastructure.
- [x] Install AWS dependencies, run `pip check` and SDK-construction check in GitHub CI.
- [x] Complete a real Strands/Bedrock tool invocation and save evidence ([run](https://github.com/babifarah9/decisionpilot-ai/actions/runs/34779404240)).
- [x] Complete browser approval/rejection tests in model-backed mode (owner confirmed both paths).
- [x] Inspect owner-supplied desktop landing-page screenshot.\n- [ ] Validate mobile layout and collect gate/completion/rejection screenshots.
- [x] Verify GitHub license detection and passing CI on the initial source release.
- [x] Produce captioned video using genuine recorded approval/completion and rejection.
- [x] Receive uploaded YouTube URL from owner: https://youtu.be/txn8iroBFnw.
- [ ] Confirm YouTube visibility is Public (not Unlisted/Private) and signed-out playback works.
- [x] Deploy public HTTPS demo; launcher origin health passed in Bedrock mode.\n- [ ] Complete deployed restart persistence/session-isolation checks and review remaining credits.
- [ ] Replace any draft-status/link instructions in published materials with actual outcomes.
- [ ] Review every Devpost field, attach assets and click final submit before the deadline.

## Evidence integrity

`docs/assets/offline-audit.json` is explicitly synthetic, including its attention duration. The model-backed evidence file must come from `scripts/bedrock_smoke.py` using authorized credentials. A test harness or deterministic simulation is not proof of live Strands reasoning. Successful packaging is not proof of deployment. A guessed repository or demo URL is not an artifact.
