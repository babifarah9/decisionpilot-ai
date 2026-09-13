# Public AWS demo: reviewed CloudShell deployment

Status: **prepared; not yet deployed or validated in AWS**. Live Strands/Nova planning passed on September 13, 2026 ([run](https://github.com/babifarah9/decisionpilot-ai/actions/runs/34779404240)).

## What this creates

One `t3.small` EC2 host (standard CPU credits, preventing surplus-credit charges), 12 GB encrypted gp3 root storage, an Elastic IP, dedicated VPC/subnet/internet gateway, CloudFront HTTPS, and an instance role limited to Nova Lite inference plus Systems Manager administration. No SSH, key pair, NAT gateway, load balancer, custom domain or access keys are required. The GitHub smoke-test role is unchanged.

CloudFront supplies a public `https://….cloudfront.net` URL. Caching is disabled; all viewer headers and cookies reach the controller. The launcher sets the exact HTTPS origin before starting the app, enabling Secure cookies and exact-origin CSRF checks. Inbound origin traffic is limited to AWS's CloudFront origin-facing prefix list; this list is shared by CloudFront customers, not exclusive to this distribution. CloudFront-to-origin transport uses HTTP. Use this only with synthetic demo data; stronger origin authentication and TLS are needed before real personal or payment data.

SQLite lives at `/var/lib/decisionpilot/workflows-v2.db` and survives service/instance restarts. **Stack deletion or host replacement destroys the root volume and database.** Export required audit evidence first. The Elastic IP keeps the public origin address stable across stop/start.

## Review and deploy

1. Open AWS CloudShell in **us-east-1** using the intended account. The existing GitHub role cannot create this infrastructure; use your authorized console identity.
2. Download this repository at the exact reviewed commit, unzip it, and enter the project directory. The assistant's handoff supplies the pinned commands.
3. Install the launcher dependency in an isolated environment: `python3 -m venv /tmp/decisionpilot-launcher`, then `/tmp/decisionpilot-launcher/bin/python -m pip install boto3`. Use `/tmp/decisionpilot-launcher/bin/python` instead of `python3` for the launcher commands below. Do not use `--user` inside a virtual environment. Run `python3 deploy/deploy_aws.py --source-commit <40-character-reviewed-commit>`.
4. The script validates the template and prepares a **CREATE change set** without launching compute. Review the printed account, resources and CloudFormation change set. Only type `DEPLOY` if you approve creation, public hosting and metered usage.
5. Wait for stack creation and instance configuration. Share the printed **Demo URL**. The origin health check does not replace browser approval/rejection testing.

Do not run a second CREATE if setup fails. Inspect CloudFormation Events and EC2 system logs. If the stack is `CREATE_COMPLETE` but boot/configuration needs retry, run the same command with `--resume`; it asks for `CONFIGURE` and reruns only host configuration. Read bootstrap errors in `/var/log/cloud-init-output.log` through Systems Manager. The service remains stopped if installation fails or its environment file is missing.

## Cost and lifetime

Planning estimate for us-east-1: t3.small $0.0208/hour (~$15.18/730 hours), one IPv4 $0.005/hour (~$3.65), 12 GB gp3 ~$0.96/month: **about $20/month before model calls, transfer and other usage**. Confirm prices and available credits in your account before executing. CloudFront/request charges depend on traffic and account plan. No free-tier eligibility is assumed. The 30 daily cloud-task limit is global and persistent; it is not a dollar cap. Model calls are separately bounded per task. Unused public access can exhaust the daily allowance.

Keep the demo available through the official judging access period if submitted. After judging, export audit evidence, then delete the `decisionpilot-public-demo` CloudFormation stack to release compute, storage, distribution and address. Stopping EC2 alone continues storage/IPv4 charges. Do not delete the separate Bedrock test-role stack accidentally.

Sources: [EC2 T3 pricing](https://aws.amazon.com/ec2/instance-types/t3/), [VPC IPv4 pricing](https://aws.amazon.com/vpc/pricing/), [EBS pricing](https://aws.amazon.com/ebs/pricing/), [CloudFront pricing](https://aws.amazon.com/cloudfront/pricing/), [disabled caching policy](https://docs.aws.amazon.com/AmazonCloudFront/latest/DeveloperGuide/using-managed-cache-policies.html), [viewer forwarding policy](https://docs.aws.amazon.com/AmazonCloudFront/latest/DeveloperGuide/using-managed-origin-request-policies.html).

## Acceptance checks after deployment

- `/health` reports `bedrock`; the UI displays the cloud mode and simulated providers.
- Create a task; autonomous steps end in `WAITING_FOR_HUMAN` with no receipt.
- Human clicks Approve; observe approval, execution, verification and completion with estimated minutes saved.
- Reject another task; confirm no receipt or savings credit.
- Refresh a pending task; retain its state. Use a fresh private browser window to check session isolation.
- Verify desktop and phone layout; capture actual screenshots/video.
- Restart the service through SSM and confirm durable state remains.
- Do not describe AgentCore as deployed: this stack runs Strands directly on EC2 with Bedrock. The optional AgentCore planner remains a separate deployment.
