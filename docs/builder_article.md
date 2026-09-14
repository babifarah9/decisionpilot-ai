# Agents for Humans: Building DecisionPilot AI with a Human-Only Approval Gate

*By Bassem Abi-Farah*

An annual car-service booking sounds simple. In practice, it means checking providers, comparing prices and ratings, finding a suitable appointment, and confirming the details. Most of that work is repetitive preparation. The final commitment is the part that deserves human attention.

I built **DecisionPilot AI** for the AWS Agents for Humans hackathon to help busy individuals and families delegate that preparation while keeping control over spending and commitments.

The idea is straightforward: **your agent does the work; you make the call.**

## One objective, one meaningful decision

The first workflow begins with a familiar request:

> Schedule my annual car service under $180. I prefer a morning appointment and want the best balance of rating and price.

The user confirms the budget and appointment preference. DecisionPilot then searches the available options, evaluates the tradeoffs, and proposes the strongest eligible appointment.

Its Human Decision Gate shows the provider, appointment time, price, recommendation rationale, and alternatives. The workflow pauses until the person explicitly approves or rejects the proposal.

Approval enables execution of that specific proposal, followed by receipt verification. Rejection ends the workflow without a booking. Throughout the process, the interface displays progress and maintains an audit trail.

The demonstration uses fictional providers, illustrative USD prices, and simulated bookings. No garage is contacted and no payment is made. The AI planning, decision controls, persistence, and verification logic are implemented and working.

## Building with Strands Agents SDK

DecisionPilot uses the **Strands Agents SDK** with **Amazon Nova Lite through Amazon Bedrock**. Each objective receives a fresh agent instance with two custom tools:

- **Search appointments:** retrieve candidate appointments from the synthetic inventory.
- **Evaluate appointments:** compare candidates against the confirmed constraints and scoring rule.

The agent plans its tool use and returns a structured recommendation containing the plan, selected candidate, and explanation.

A separate application controller validates that recommendation. It checks that the required tools were used, that the appointment exists in the trusted inventory, and that it meets the confirmed budget and morning constraint. Eligible appointments are ranked using equal weights for normalized rating and remaining budget headroom.

This separation makes model reasoning useful without treating every model response as an executable instruction.

## Why the agent cannot approve itself

The central safety decision was to keep both approval and execution out of the agent's tool set.

After planning, the controller saves an exact proposal, fingerprints its contents, and places the workflow in a waiting-for-human state. The planning invocation ends.

The human's browser submits approval or rejection to the controller outside the autonomous agent loop. The controller checks session ownership, proposal identity, and expiration before recording the decision. Approval authorizes a specific appointment at a specific price.

The executor accepts only an approved, unchanged, unexpired proposal. A unique proposal key prevents duplicate simulated bookings during retries or concurrent requests. The verifier then compares the receipt against the approved provider, appointment, and price. A mismatch prevents completion.

These controls enforce the boundary between autonomous preparation and human authorization. Real paid bookings would also require authenticated user accounts and a securely integrated provider.

## From planning to a live AWS application

The public demo runs on **Amazon EC2**, with **Amazon CloudFront providing HTTPS**. **SQLite** stores workflow state, proposals, simulated receipts, and audit events on encrypted **Amazon EBS** storage. Retaining the database volume preserves state across application restarts.

AWS IAM roles provide service access without embedding static AWS keys in the application. AWS Systems Manager supports host administration, and AWS CloudFormation defines the deployment infrastructure.

For validation, GitHub Actions assumed a restricted AWS role through OpenID Connect and ran a real Strands/Bedrock planning invocation. The test reached the Human Decision Gate without executing a booking. The recorded public demonstration shows both approval followed by verified completion and rejection without a booking.

## Making the attention budget visible

DecisionPilot includes a **Human Attention Budget** to show the intended benefit of delegation.

It subtracts active browser interaction time from a user-supplied estimate of the task's usual manual effort. The default baseline is 35 minutes and can be changed. Hidden tabs and extended inactivity do not accumulate attention time. Estimated savings appear only after successful verification.

In the recorded demonstration, the interface displayed **33.8 estimated minutes saved**, based on a 35-minute manual baseline and 74 seconds of active attention.

This figure is an illustrative estimate, not a measured productivity gain. Keeping the baseline and interaction time visible lets people understand how the result was calculated.

## Challenges and lessons learned

The most demanding work was turning “ask the human first” into enforceable application behavior.

That required handling expired proposals, replayed decisions, concurrent execution, task ownership, and receipt mismatches. It also meant separating durable workflow state from individual agent invocations.

DecisionPilot passes **32 automated lifecycle and HTTP tests** covering approval, rejection, unauthorized access, concurrency, expiration, tampering, restart persistence, and verification failures. Live Bedrock validation and recorded browser workflows provide additional evidence beyond the deterministic tests.

The main lesson is that dependable autonomy requires more than a good recommendation. Approval must be specific, execution must tolerate retries, and completion must follow verification.

## What comes next

The next step is a real provider integration with authenticated users, fresh quotes, provider-side duplicate protection, and independent receipt verification. Stronger origin security and operational monitoring will accompany that work before the application handles real personal or payment data.

Additional administrative workflows will follow once the car-service experience is reliable.

DecisionPilot brings a practical principle to everyday AI: reduce repetitive supervision while preserving the human decision that matters.

## Explore DecisionPilot AI

- [Try the live application](https://d2bjqcxkm4ezmd.cloudfront.net)
- [Watch the demonstration](https://youtu.be/txn8iroBFnw)
- [Explore the source code](https://github.com/babifarah9/decisionpilot-ai)
- [View the deployed AWS architecture](https://github.com/babifarah9/decisionpilot-ai/blob/main/docs/live-architecture.md)

DecisionPilot AI is released under the MIT license. It was developed from a starter package with AI coding assistance. Third-party SDKs retain their respective licenses.
