# DecisionPilot AI

**Tagline:** Your agent does the work. You make the call.

**Track:** Everyday Agents  
**Built with:** Python, Strands Agents SDK, Amazon Bedrock integration, optional Amazon Bedrock AgentCore entrypoint, SQLite, HTML, CSS and JavaScript.

## Inspiration / problem

Small administrative tasks consume far more attention than their final decision deserves. Scheduling a car service means checking providers, comparing prices and ratings, choosing a time, and confirming the booking. The person should not have to supervise every search step, but handing an AI unrestricted authority to spend money is the wrong tradeoff.

DecisionPilot AI explores a practical alternative: automate the preparation, then ask for a clear human decision at the moment it matters.

## What it does

The focused MVP takes an annual car-service objective and confirmed constraints, evaluates candidate appointments, and recommends the strongest eligible option. It then stops at a Human Decision Gate showing the exact provider, appointment, price, rationale and alternatives.

Approval resumes execution of that specific proposal. Rejection stops the workflow without a booking. After execution, a verification step compares the provider receipt against the approved details. The UI shows each stage, an audit trail, and estimated human minutes saved.

The hackathon sandbox uses fictional providers, illustrative USD prices and simulated bookings. It does not contact a real garage or process payment. The workflow, persistence, approval checks and receipt comparison run as application code.

## Who it is for

Busy individuals and families who want help with everyday administration while retaining control over spending and commitments. The car-service workflow is deliberately narrow so the complete decision lifecycle can be demonstrated clearly.

## Why it matters

Useful autonomy should reduce the number of things a person must monitor. A long chat that leaves someone to complete the original task is not enough. Equally, a system that can authorize its own consequential actions undermines trust. DecisionPilot focuses on a meaningful boundary: preparation can be autonomous; commitment requires a human decision.

## How it works

1. The user describes the objective and confirms budget and appointment preferences.
2. The planner searches a synthetic inventory and evaluates price/rating tradeoffs.
3. The controller independently validates the recommendation and saves an expiring proposal.
4. The workflow becomes `WAITING_FOR_HUMAN`; no booking exists.
5. A separate human-only controller accepts an explicit approve or reject action from the owning browser session.
6. Approval enables idempotent simulated execution. Verification then checks the receipt before completion is declared.
7. State and audit events remain available across refreshes and host restarts when the database volume is retained.

## How Strands Agents SDK is used

In AWS mode, a fresh Strands `Agent` uses `BedrockModel` and two custom `@tool` functions: `search_appointments` and `evaluate_appointments`. The model plans its tool use and returns a typed recommendation through structured output. The application checks both tool use and the selected candidate before accepting the result. A model-call budget and bounded output reduce uncontrolled usage.

Neither approval nor execution is an agent tool. The agent never receives the browser's ownership token. The offline demonstration uses deterministic planning and is explicitly labeled; it is not represented as an LLM invocation.

## AWS architecture

The Bedrock integration uses a configurable model, initially Amazon Nova Lite in `us-east-1`. The optional AgentCore entrypoint hosts only the stateless planner. The UI, human decision controller and transactional state remain on a persistent host, with an EC2/EBS deployment path and HTTPS proxy configuration supplied.

Cloud deployment and live model validation are pending account authorization. No AgentCore or live-hosting claim is made in this submission draft.

## Human Decision Gate

Approval is outside the autonomous loop. The controller verifies session ownership before mutation, requires an explicit boolean decision, binds it to a fingerprinted proposal, rejects replayed decisions, enforces expiration, and prevents execution until approval exists. A unique proposal key prevents duplicate simulated bookings, including concurrent requests. Receipt mismatches withhold completion.

The threat boundary is the agent's permitted capabilities and the session-aware controller. A compromised server, database administrator or stolen browser session is not covered by this demonstration.

## Human Attention Budget

The user supplies a manual-effort baseline; the UI counts active browser time spent entering the objective and reviewing the decision, excluding hidden tabs and extended inactivity. Estimated minutes returned equal the baseline minus that active time, credited only after successful verification.

A 35-minute baseline and one minute of attention would imply 34 estimated minutes saved. This is a transparent illustrative estimate, not an empirical productivity result.

## Challenges

The main engineering challenge was turning a prompt-level promise into an enforced state transition. We addressed replayable decisions, duplicate execution, task ownership checks, shared agent state, quote expiration and false completion after failed verification. We also separated persistent human decisions from potentially ephemeral cloud runtime sessions.

The build environment blocked AWS dependency installation and local browser access, so the package includes explicit SDK, cloud and visual validation steps rather than presenting those checks as completed.

## Accomplishments

The focused car-service lifecycle works through a local HTTP controller and persistent database. Thirty-two automated lifecycle and HTTP tests pass, including concurrent approvals/execution, rejection, unauthorized access, expiry, tampering, restart recovery, CSRF and receipt mismatch. The package contains the UI, architecture assets, MIT license, setup instructions and an opt-in Bedrock smoke test.

## What was learned

The quality of an autonomous workflow depends on its boundaries and recovery behavior as much as its reasoning. An approval should authorize a specific immutable proposal, not a vague intention. Completion should follow verification. Time-savings claims should distinguish measured interaction time from an assumed baseline.

## What is next

First, complete authorized Bedrock validation, visual QA and public deployment, then record the working demo. After the hackathon, integrate a real service provider with authenticated users, fresh quotes, provider-side idempotency and external receipt verification. Additional workflows will follow only after the car-service experience is reliable.

## Attribution and build disclosure

Developed from the entrant-supplied DecisionPilot starter package with AI coding assistance. The entrant must confirm that the project was created during the competition period and disclose any earlier work. Application source is MIT licensed; third-party SDKs retain their respective licenses. All appointment data is synthetic.
