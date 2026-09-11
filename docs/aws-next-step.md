# Next step: authorize one live Bedrock test

GitHub source publication, MIT detection, both Python safety jobs and the actual SDK-install/construction job have succeeded:
https://github.com/babifarah9/decisionpilot-ai/actions/runs/34615901169

Live AWS inference has not yet run. A manual GitHub workflow is prepared so no access keys need to be copied into GitHub or chat.

## Owner actions

1. Sign in to the intended AWS account. Confirm the hackathon credit balance and model access in **us-east-1**.
2. In **CloudFormation**, create a stack in us-east-1 using `deploy/github-bedrock-role.json`. Review the IAM resources before authorizing creation. If the account already has an OIDC provider for `token.actions.githubusercontent.com`, supply its ARN in `ExistingOidcProviderArn`; otherwise leave that field blank. Acknowledge IAM resource creation only after review.
3. When the stack finishes, copy **GitHubRoleArn** from Outputs.
4. In this repository's **Actions → Live Bedrock validation → Run workflow**, select `main`, enter that ARN and check the metered-call authorization box. Run the workflow.

The role uses GitHub’s current immutable owner/repository IDs in the OIDC subject and trusts only this repository's main branch and grants only Nova Lite invocation in us-east-1. Anyone who can change/run trusted main-branch workflows can use this role, so review repository collaborator access. The ARN is an identifier, not a credential; no access key or secret is requested. No AWS service deployment or garage booking occurs in this test.

The test must show a real Strands search/evaluation, a valid pending proposal and no executed booking. It stores a synthetic-objective evidence artifact. The planner is limited to six model calls, bounded output and a five-minute CI job; this is not an exact dollar cap. Check model pricing/credits before authorization. The workflow runs only manually with an explicit checked authorization input; ordinary pushes do not invoke AWS.

If the selected model requires different account/region/profile access, the test may fail safely. Share the workflow run URL for diagnosis. Do not grant broader AWS permissions to conceal an access error.

After the live test passes, we can prepare the chosen public demo/AgentCore deployment against your approved budget. This test role cannot provision that infrastructure.

Reference: [GitHub OIDC for AWS](https://docs.github.com/en/actions/how-tos/secure-your-work/security-harden-deployments/oidc-in-aws).
