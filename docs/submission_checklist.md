# Submission checklist

**Release decision: NOT YET SUBMISSION-READY.** The offline build passes; real SDK/AWS validation and required public artifacts remain unfinished.

Official requirements checked September 11, 2026: [rules](https://agentsforhumans.devpost.com/rules) and [overview](https://agentsforhumans.devpost.com/).

| Requirement | Status / evidence |
|---|---|
| Submit by September 14, 2026, 5 PM PDT | Pending; September 15, 00:00 UTC |
| Eligible entrant; truthful residence/domicile | Owner confirmation; Quebec is excluded |
| New project during competition; disclose earlier work | Owner confirms starter provenance |
| Working Strands project | Integration written; live validation blocked |
| Public source repository, README and MIT/Apache license | Source included in this public repository; check Actions |
| Architecture diagram | PNG, SVG and Mermaid ready |
| Description | `submission_draft.md` ready for review |
| Public YouTube/Vimeo video, ≤5 minutes | 4:35 script ready; recording/upload pending |
| AWS Builder ID | Owner supplies |
| Free judging access through October 8 | Offline build ready; test public access |
| English materials and rights clearance | Drafts English; owner confirms rights |
| Optional live demo / AgentCore | Not deployed |
| Optional public Builder article with Agents for Humans title | Draft ready; publication pending |

## Product release gates

- [x] Core and HTTP lifecycle tests pass.
- [x] Agent tool set contains no approval or execution capability.
- [x] Ownership checked before decision mutation.
- [x] Approval/rejection, expiration, replay and concurrent execution tested.
- [x] Persistent state, audit and simulated receipt verification implemented.
- [x] Secrets excluded from release package; heuristic scan passes.
- [x] Architecture distinguishes current code from optional cloud infrastructure.
- [ ] Install AWS dependencies, run `pip check` and SDK-construction check.
- [ ] Complete a real Strands/Bedrock tool invocation and save evidence.
- [ ] Complete browser approval/rejection tests in model-backed mode.
- [ ] Validate desktop/mobile layouts and collect actual screenshots.
- [ ] Verify GitHub license detection and passing CI on this source release.
- [ ] Record public video without fabricated model results or deployment claims.
- [ ] If hosting, verify HTTPS, persistence, session isolation and spend controls.
- [ ] Replace any draft-status/link instructions in published materials with actual outcomes.
- [ ] Review every Devpost field, attach assets and click final submit before the deadline.

## Evidence integrity

`docs/assets/offline-audit.json` is explicitly synthetic, including its attention duration. The model-backed evidence file must come from `scripts/bedrock_smoke.py` using authorized credentials. A test harness or deterministic simulation is not proof of live Strands reasoning. Successful packaging is not proof of deployment. A guessed repository or demo URL is not an artifact.
