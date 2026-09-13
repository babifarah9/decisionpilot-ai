# Agents for Humans: Building DecisionPilot AI with a Human-Only Approval Gate

*Draft for owner review. Live Bedrock validation passed; update the deployment-status paragraph after public hosting is verified. Do not describe an untested cloud path as deployed.*

An annual car-service booking sounds simple. In practice, it involves checking providers, comparing prices, evaluating ratings, finding a suitable appointment, and confirming the details. Most of that is repetitive preparation. The final commitment is the part that deserves human attention.

I built DecisionPilot AI around that distinction for the AWS Agents for Humans hackathon. The goal is a focused Everyday Agent: receive an objective, prepare a defensible recommendation, and interrupt the person only when a decision is necessary.

## A deliberately narrow first workflow

The MVP starts with: “Schedule my annual car service under $180. I prefer a morning appointment and want the best balance of rating and price.” The user confirms the budget and daypart in the interface.

The demo inventory contains four fictional appointments. A disclosed scoring rule gives equal weight to rating and remaining budget headroom. Budget and the morning preference are constraints. The strongest eligible appointment is presented with its price, rating, rationale and alternatives.

All bookings are simulated. That lets us exercise state transitions, explicit decisions, duplicate protection and verification without pretending to have a garage API or taking payment.

## Where Strands fits

The AWS path creates a fresh Strands Agent for each objective. Its Bedrock model is configurable, initially Amazon Nova Lite. The agent receives two custom tools: one to search appointments and one to evaluate them. Structured output returns the plan, selected candidate and explanation.

The controller does not blindly trust the recommendation. It verifies that the required tools were used and checks the selected candidate against trusted inventory and the confirmed constraints. A malformed or invalid recommendation fails safely. The interface does not substitute offline success if AWS returns an error.

I kept the tool set deliberately small. There is no generic shell, filesystem or arbitrary network tool. Most importantly, there is no approve function and no execute function registered with the agent.

## Approval is a separate capability

A prompt saying “ask first” is not the whole safety design. DecisionPilot's controller persists an exact proposal, fingerprints its contents, and enters `WAITING_FOR_HUMAN`. The planning invocation ends.

The human's browser then sends an explicit decision to a separate controller. It checks session ownership before changing state, rejects stale or replayed decisions, and records approval or rejection transactionally. Approval authorizes one specific appointment at one specific price.

The executor accepts only that approved, unchanged, unexpired proposal. A unique proposal key prevents duplicate simulated side effects during retries and concurrent requests. The verifier compares the provider receipt with the approved details. A mismatch withholds completion.

This protects the boundary between the autonomous agent and the human decision. It does not claim to protect against a compromised trusted host or a stolen browser session. Real paid bookings would require stronger user authentication and provider integration.

## Persistence and AWS deployment choices

SQLite stores the workflow, audit events and simulated receipts on a persistent controller-host volume. That is appropriate for a single-host hackathon demo and survives process restarts when the volume is retained.

The optional AgentCore entrypoint hosts only the stateless planner. It never receives the browser's session token or exposes an approval action. Keeping durable human decisions outside ephemeral runtime storage avoids losing approvals as sessions end or compute scales.

The package includes an EC2/EBS hosting path and HTTPS container configuration. On September 13, 2026, the real Strands/Nova planning test passed using a restricted AWS role assumed through GitHub OIDC. It reached the human gate without executing a booking. AgentCore and public hosting remain pending. A reviewed CloudFormation/CloudShell deployment is prepared.

## Measuring attention without overstating it

The Human Attention Budget subtracts active browser interaction time from a user-supplied manual baseline. The baseline starts at 35 minutes but is editable. Hidden tabs and extended inactivity do not accumulate attention time. Estimated savings are credited only after verification.

This is a product feedback mechanism, not a research result. It makes assumptions visible and avoids claiming that an arbitrary fixed number of seconds represents actual human effort.

## What testing changed

The starter helped reveal the failure modes that matter: shared agent instances, ownership checks after mutation, repeatable approvals, duplicate execution and success messages without substantive verification.

The revised local build passes 32 lifecycle and HTTP tests. They exercise the full gate, rejection, ownership, concurrency, expiration, tampering, receipt mismatch, restart persistence and CSRF protections. Separate scripts construct the real SDK components and, with explicit AWS authorization, run a live Bedrock planning invocation. Cloud checks remain distinct from offline tests.

## Next steps

Next come visual QA, public hosting and an end-to-end demo video. A real provider adapter comes later, with authenticated identity, fresh quotes, provider-side idempotency and external receipt verification. More workflows can wait until this one is reliable.

DecisionPilot's central idea is simple: autonomy is useful when it removes repetitive supervision while preserving the human decision that actually matters.

**Project:** https://github.com/babifarah9/decisionpilot-ai  
**Demo:** add the tested public demo URL, if deployed.  
**Architecture:** attach `architecture/architecture.png`.  
**License:** MIT. Developed from an entrant-supplied starter with AI coding assistance; providers and receipts are synthetic.
