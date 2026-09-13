"""Run in AWS CloudShell. Prepare a change set; deploy only after typed approval."""
import argparse
import json
import re
import time
from pathlib import Path

import boto3


def configuration_commands(url):
    if not re.fullmatch(r'https://[a-z0-9]+\.cloudfront\.net', url):
        raise ValueError('Unexpected CloudFront URL')
    environment = '\n'.join([
        'HOST=0.0.0.0', 'PORT=8080', 'AWS_REGION=us-east-1',
        'DECISIONPILOT_MODE=bedrock', 'DECISIONPILOT_MODEL=amazon.nova-lite-v1:0',
        'DECISIONPILOT_DB=/var/lib/decisionpilot/workflows-v2.db',
        'DECISIONPILOT_DAILY_CLOUD_RUNS=30', 'DECISIONPILOT_PUBLIC_ORIGIN='+url,
    ])
    return [
        'set -eu',
        'for attempt in $(seq 1 90); do test -f /opt/decisionpilot/ready && break; sleep 10; done',
        'test -f /opt/decisionpilot/ready',
        "umask 077; cat > /etc/decisionpilot.env <<'ENV'\n"+environment+'\nENV',
        'systemctl restart decisionpilot',
        "for attempt in $(seq 1 30); do curl -fsS http://localhost:8080/health && exit 0; sleep 2; done; exit 1",
    ]


def configure(ssm, instance, url):
    print('Waiting for instance administration and dependency installation...')
    for _ in range(90):
        entries = ssm.describe_instance_information(Filters=[{'Key':'InstanceIds','Values':[instance]}])['InstanceInformationList']
        if entries and entries[0]['PingStatus'] == 'Online':
            break
        time.sleep(10)
    else:
        raise RuntimeError('Instance did not connect to SSM. Inspect EC2 system log; do not recreate the stack.')
    command = ssm.send_command(InstanceIds=[instance], DocumentName='AWS-RunShellScript',
        Parameters={'commands':configuration_commands(url),'executionTimeout':['1200']},
        TimeoutSeconds=1200)['Command']['CommandId']
    for _ in range(130):
        time.sleep(10)
        result = ssm.get_command_invocation(CommandId=command, InstanceId=instance)
        if result['Status'] == 'Success':
            print('Origin health check passed in Bedrock mode.')
            return
        if result['Status'] in ('Failed','Cancelled','TimedOut'):
            raise RuntimeError('Configuration failed. Inspect SSM Run Command '+command+' and /var/log/cloud-init-output.log.')
    raise RuntimeError('Configuration still running. Inspect SSM Run Command '+command)


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--source-commit',required=True)
    parser.add_argument('--stack-name',default='decisionpilot-public-demo')
    parser.add_argument('--resume',action='store_true',help='Configure an already created stack; no recreation')
    args=parser.parse_args()
    if not re.fullmatch('[a-f0-9]{40}',args.source_commit):
        parser.error('Source commit must be an exact 40-character SHA')
    session=boto3.Session(region_name='us-east-1')
    cf=session.client('cloudformation'); ssm=session.client('ssm')
    account=session.client('sts').get_caller_identity()['Account']
    print('Target account:',account,'Region: us-east-1')
    if not args.resume:
        template=Path(__file__).with_name('public-demo.json').read_text()
        cf.validate_template(TemplateBody=template)
        prefix=session.client('ec2').describe_managed_prefix_lists(Filters=[{'Name':'prefix-list-name','Values':['com.amazonaws.global.cloudfront.origin-facing']}])['PrefixLists'][0]['PrefixListId']
        change='review-'+str(int(time.time()))
        cf.create_change_set(StackName=args.stack_name,ChangeSetName=change,ChangeSetType='CREATE',
            TemplateBody=template,Capabilities=['CAPABILITY_IAM'],
            Parameters=[{'ParameterKey':'SourceCommit','ParameterValue':args.source_commit},
                        {'ParameterKey':'CloudFrontPrefixListId','ParameterValue':prefix}],
            Tags=[{'Key':'Project','Value':'DecisionPilotAI'}])
        cf.get_waiter('change_set_create_complete').wait(StackName=args.stack_name,ChangeSetName=change)
        changes=cf.describe_change_set(StackName=args.stack_name,ChangeSetName=change)
        for item in changes['Changes']:
            r=item['ResourceChange']; print(r['Action'],r['LogicalResourceId'],r['ResourceType'])
        print('\nReview this change set in CloudFormation before proceeding.')
        print('Creates t3.small (standard credits), 12 GB gp3, public IPv4, CloudFront and IAM/SSM resources.')
        print('Budget estimate: about $20/month infrastructure at light traffic, PLUS Bedrock and transfer.')
        print('Estimate is not a spending cap; confirm current prices and your remaining credits.')
        print('Deleting this stack deletes the host database. Export evidence first. No real garage bookings.')
        if input('Type DEPLOY to authorize resource creation, public hosting and metered usage: ') != 'DEPLOY':
            print('Not executed. Review-only stack/change set remains in CloudFormation.'); return
        cf.execute_change_set(StackName=args.stack_name,ChangeSetName=change)
        print('Creating infrastructure; CloudFront may take several minutes...')
        cf.get_waiter('stack_create_complete').wait(StackName=args.stack_name,WaiterConfig={'Delay':20,'MaxAttempts':90})
    else:
        if input('Type CONFIGURE to authorize configuration/restart of the existing demo host: ') != 'CONFIGURE':
            return
    stack=cf.describe_stacks(StackName=args.stack_name)['Stacks'][0]
    if stack['StackStatus'] not in ('CREATE_COMPLETE','UPDATE_COMPLETE'):
        raise RuntimeError('Stack is not complete: '+stack['StackStatus'])
    outputs={v['OutputKey']:v['OutputValue'] for v in stack['Outputs']}
    configure(ssm,outputs['InstanceId'],outputs['DemoUrl'])
    print('\nDemo URL:',outputs['DemoUrl'])
    print('Next: check this URL in a browser, approve/reject synthetic workflows, and record evidence.')
    print('This deploys EC2 + Bedrock. It does NOT deploy AgentCore.')


if __name__=='__main__':
    main()
