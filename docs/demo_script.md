# DecisionPilot AI — demo script and shot list

Target runtime: **4 minutes 35 seconds**. Maximum allowed: five minutes. Record the actual application; do not animate an unimplemented success. Keep text legible and use the approved architecture image. Use no background music unless you own the rights.

The live Strands/Bedrock test passed, the AWS demo is deployed, and the owner confirmed approval/completion and rejection. Record the deployed app at https://d2bjqcxkm4ezmd.cloudfront.net. Keep the simulated-provider disclosure visible. AgentCore is not deployed.

## Capture on your Mac

1. Open the demo in a clean browser window. Close unrelated tabs and hide personal browser chrome from the selected recording area.
2. Open this script on a second screen/device if possible. Use the actual live hosting diagram at https://github.com/babifarah9/decisionpilot-ai/blob/main/docs/live-architecture.md for the architecture shot.
3. Press Shift-Command-5, choose Record Selected Portion, and frame the app. Under Options, select your microphone if reading the narration live. Otherwise capture silent footage for later narration.
4. Record the actions in the table. Pause on each important state for 5–10 seconds. Scroll slowly so proposal details, receipt, audit and savings are legible.
5. Stop the recording from the menu bar. Upload the resulting MOV or MP4 to this conversation for review/editing. Raw clips may exceed five minutes; the final export must not.
6. If recording separate clips, capture objective/planning/gate, approval/completion, rejection, and architecture/tests. Do not approve until the gate is clearly visible.

The working-demo footage is still required. A generated promotional video or the single landing-page screenshot cannot establish the end-to-end workflow.

| Time | Shot / action | Voiceover |
|---|---|---|
| 0:00–0:25 | Open on the application title and objective form. | “Everyday administration steals time through small decisions and repetitive checking. DecisionPilot AI is for busy people who want an agent to handle the preparation while they keep control over spending and commitments.” |
| 0:25–0:50 | Show the objective, $180 budget and morning preference. | “Here is one complete workflow: schedule my annual car service under 180 dollars, in the morning, balancing rating and price. This is a sandbox: providers, prices and bookings are simulated. The decision lifecycle is implemented in code.” |
| 0:50–1:20 | Click **Find my best appointment**. Show progress and candidate table. | “This deployed agent uses Strands with Amazon Bedrock and two read-only tools to search and compare appointments. Confirmed budget and time preferences are enforced independently. The disclosed score gives equal weight to normalized rating and price headroom.” |
| 1:20–1:55 | Show pending gate, $139 recommendation, 4.7 rating, 08:30 slot, rationale and alternatives. | “Here is the recommended provider, price and morning appointment. I can compare its rating and price against the alternatives. Now the agent stops. There is no booking yet. I can inspect exactly what I would approve.” |
| 1:55–2:20 | Switch to architecture, then show `tools.py` briefly. | “The agent has no approval tool and no execution tool. Approval comes from a separate controller that validates the browser session and this exact proposal. The model cannot turn its own text into permission.” |
| 2:20–2:55 | Return to UI and click **Approve simulated booking**. Show completion and audit. | “My explicit approval resumes execution. A unique proposal key prevents duplicates. Verification compares the simulated provider receipt against the approved provider, appointment and price. Only then does the workflow report completion.” |
| 2:55–3:20 | Show attention budget and receipt. | “The attention budget makes the benefit visible. The manual baseline is an estimate I can change. The browser counts active interaction time. Estimated savings appear only after verification; they are not presented as an empirical productivity result.” |
| 3:20–3:45 | Start a second workflow, click **Reject**, show no booking. | “Control also means saying no. Rejection records the decision and ends the workflow without a booking. An expired or already decided proposal cannot be reused.” |
| 3:45–4:10 | Show test output, then architecture. | “The safety and HTTP tests cover replay, concurrent execution, ownership, expiration, tampering and verification failure. The live app runs on EC2, with SQLite state and audit on encrypted EBS, CloudFront for HTTPS, and Amazon Bedrock for inference. AgentCore is an optional future deployment.” |
| 4:10–4:35 | End on completed UI and actual repository/demo links. | “DecisionPilot AI reduces routine supervision while preserving a meaningful human decision. Next comes a real provider integration after authenticated identity and provider verification are in place. Your agent does the work. You make the call.” |

## Recording checklist

- Use real observed results. Do not read an invented confirmation or time-savings number.
- Capture the model-backed flow after validation. Keep “Offline demonstration” visible if recording offline.
- If waiting for a model response, trim dead time and label the cut; do not imply an unmeasured response time.
- At 1080p, zoom enough that gate details, alternatives and status are readable.
- Record approval and rejection separately; show the actual UI state for both.
- Hide AWS account IDs, credentials, browser profiles, private tabs and personal data.
- Only say “deployed on AgentCore” after a successful deployed invocation; otherwise call it an optional architecture path.
- Show the actual public GitHub URL after publication, never a placeholder.
- Export an English MP4 under five minutes. Upload to YouTube or Vimeo and set it **public** after owner review.

## Screenshot shot list

1. Objective and constraints (initial UI).
2. Pending Human Decision Gate with all alternatives.
3. Verified completion, simulated confirmation and attention estimate.
4. Rejected workflow with no booking.

The owner supplied a desktop landing-page screenshot. Capture gate, completion and rejection from the live recording; remove browser-profile details before publishing screenshots. Do not substitute generated mockups.

## Publishing copy

**YouTube/Vimeo title:** DecisionPilot AI | Agents for Humans | Human-Controlled Autonomy

**Description:** DecisionPilot AI handles the preparation for an annual car-service appointment, compares rating and price, and stops for explicit human approval. Built with Strands Agents SDK and Amazon Bedrock, deployed on EC2 with CloudFront HTTPS and persistent SQLite/EBS state. The agent has no approval or execution tools. Providers and bookings are simulated; AI planning is real. Estimated attention savings use a disclosed manual baseline.

Live demo: https://d2bjqcxkm4ezmd.cloudfront.net
Source and MIT license: https://github.com/babifarah9/decisionpilot-ai
Track: Everyday Agents — AWS Agents for Humans

Publish only after owner review; set visibility to Public and paste the video URL into Devpost. Do not claim AgentCore deployment.
