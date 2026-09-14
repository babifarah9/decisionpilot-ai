# DecisionPilot AI — narrated demo

Target runtime: approximately 2 minutes 40 seconds, with a clear English voice at 135–145 words per minute. Use the original screen recording, readable crops of the working application, and the current architecture graphic.

## Voiceover and shots

### 0:00–0:18 — Problem and promise

Everyday administration takes more than time. It takes attention: searching, comparing, checking details, and deciding what to do next. DecisionPilot AI handles the repetitive work and pauses when your judgment matters. Your system does the work. You make the call.

Show the product title, then the actual objective form.

### 0:18–0:39 — The objective

Here is the task: schedule my annual car service for under one hundred and eighty dollars. I prefer a morning appointment and want the best balance of rating and price. I enter the objective, confirm the budget and appointment preference, and start the search.

Show the budget and morning preference at a readable size, followed by the actual search click.

### 0:39–1:00 — Autonomous search

DecisionPilot uses the Strands Agents SDK with Amazon Bedrock to search and evaluate the available options. In this demo, the appointment inventory is synthetic, while the cloud reasoning is real. The system checks the confirmed constraints and presents a recommended appointment with its price, rating, reasoning, and alternatives.

Show the real planning sequence and recommendation. Hold a close-up of the price and alternatives.

### 1:00–1:24 — Human Decision Gate

This is the Human Decision Gate. The workflow is waiting for me. Nothing has been booked. The planning service has only read-only search and evaluation tools. It has no tool that can approve or execute its own proposal. My approval happens through a separate controller, outside the autonomous planning loop.

Hold the pending state and both decision buttons. Use the current architecture graphic for the separate approval path.

### 1:24–1:45 — Approval and verification

When I approve, the controller resumes the workflow and creates a simulated booking. It then checks the receipt against the exact proposal I approved, including the provider, appointment slot, and price. Only successful verification enables completion. The workflow records the decision and execution events in its audit trail.

Show the actual approval click, followed by the completed state, receipt and audit events. Do not insert a fabricated intermediate screen.

### 1:45–2:03 — Human Attention Budget

The Human Attention Budget shows estimated time returned. It subtracts active human attention from a manual effort baseline. This is an estimate, and savings are credited only after verification. The aim is to make the cost of human involvement visible, alongside the result.

Show the actual attention panel. Do not replace the recorded values with invented numbers.

### 2:03–2:17 — Rejection

I can also reject a proposal. In a separate workflow, rejection records my decision and stops without booking. Human control is part of the execution design.

Show the real rejection click and rejected audit state.

### 2:17–2:42 — Architecture and close

The application runs on Amazon EC2 behind CloudFront, with Amazon Bedrock providing model inference. SQLite stores workflow state and audit events on encrypted Amazon EBS. This sandbox contacts no garage and makes no payment. DecisionPilot AI demonstrates a practical principle: automate the routine work, preserve meaningful human decisions, and verify the outcome.

Show the current architecture, then the live-demo and repository links.

## Export specification

- Preserve the original recording's detail. Do not upscale and claim that missing text detail has been recovered.
- Use native-resolution crops around the objective, recommendation, decision buttons, receipt and attention panel. Re-record any view that remains unreadable.
- Deliver 1920 × 1080, 30 fps H.264 MP4 with high-quality encoding; keep a higher-resolution master if the source supports it.
- Add a natural English voiceover, paced to the actual actions, with short pauses at approval and rejection. No background music is needed.
- Normalize narration consistently, with no clipping. Include synchronized captions in a separate subtitle file.
- Hold key states long enough to read. Label any slowed footage or shortened waiting periods.
- Review the complete exported MP4 at normal playback size for text clarity, audio presence, synchronization and a runtime under five minutes.

## Project links

- Live demo: https://d2bjqcxkm4ezmd.cloudfront.net
- Repository: https://github.com/babifarah9/decisionpilot-ai
- Architecture: https://github.com/babifarah9/decisionpilot-ai/blob/main/architecture/architecture.png
