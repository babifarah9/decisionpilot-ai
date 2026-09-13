# Live AWS architecture

Demo: https://d2bjqcxkm4ezmd.cloudfront.net

The owner deployed EC2/CloudFront successfully and confirmed both browser decision paths. AgentCore is an optional planner adapter and is **not deployed**.

```mermaid
flowchart TD
    U["Human / browser"] --> C["CloudFront HTTPS"]
    C --> H["EC2 UI and controller"]
    H --> S["Strands planner"]
    S <--> B["Amazon Bedrock / Nova Lite"]
    S --> T["Read-only search and evaluation tools"]
    T --> S
    S --> G["Pending Human Decision Gate"]
    G --> U
    U --> D["Explicit approval or rejection"]
    D --> H
    H --> E["Execute approved simulated booking"]
    E --> V["Verify receipt"]
    V --> A["Completion and attention savings"]
    H <--> DB["SQLite state and audit / encrypted EBS"]
    G --> DB
    E --> DB
    V --> DB
    M["AWS Systems Manager"] --> H
```

The agent has no approval or execution tools. Approval is submitted through the owning browser session to the separate controller. Rejection records a terminal decision without executing. Persistent state stays on the EC2 host, outside the autonomous planning loop.

CloudFront caching is disabled and browser cookies/headers are forwarded. Viewer traffic uses HTTPS; the CloudFront-to-EC2 origin uses HTTP restricted by the CloudFront managed prefix list. The host uses IMDSv2 and an instance role for Nova inference; no static AWS keys are installed. This single-host synthetic demo requires stronger origin protection and authenticated user accounts before handling real personal or payment data.

Database state survives restarts. Deleting or replacing the host deletes its root EBS volume; export evidence first. Provider inventory, prices and receipts are simulated even though the Strands/Bedrock reasoning is real.
