#!/usr/bin/env python3

# The purpose of this script is to run a specific API Call
# that does not require any arguments in every Organizations
# Member Account across all supported Regions.
# Note: you must run this script in an Organizations Master Account

# Each Member Account must have an OrganizationAccountAccessRole
# or other Role in each Member Account that trusts the IAM Entity running this script
# to assume that Role. The Member Account's Role names must match the string
# provided to the variable ORGS_ACCESS_ROLE_NAME. The OrganizationAccountAccessRole 
# must have the proper IAM permissions to run the Action in ACTION_NAME

import boto3
ORGS_ACCESS_ROLE_NAME = 'OrganizationAccountAccessRole'

SERVICE_NAME = 'ec2'
ACTION_NAME = 'describe_subnets'

# list of accounts that you want to exclude
EXCLUDED_ACCOUNT_IDS = ['720840927657', '414899279353', '946508719051']

# list of regions to run script in
service_regions=boto3.session.Session().get_available_regions(SERVICE_NAME)
# disable above and set manually if specific action 
# doesn't support all the regions that the Service does
# uncomment the next 3 lines to set regions manually
# regions = 'ap-south-1 ap-northeast-2 ap-southeast-1 ap-southeast-2 ap-northeast-1 ca-central-1 \
# eu-central-1 eu-west-1 eu-west-2 eu-west-3 sa-east-1 us-east-1 us-east-2 us-west-1 us-west-2'
# service_regions = regions.split()

# remove regions that are not enabled
service_regions.remove('ap-east-1')
service_regions.remove('me-south-1')

continue_on_error = None

orgs = boto3.client('organizations')

try:
    organization = orgs.describe_organization()['Organization']
except Exception as e:
    print(e)
    exit(1)

master_account_id = organization['MasterAccountId']

try:
    account_ids = []
    paginator = orgs.get_paginator('list_accounts')
    print('Accounts: ')
    for page in paginator.paginate():
        for account in page['Accounts']:
            account_ids.append(account['Id'])
            print(account['Id'])
except Exception as e:
    print(e)

sts = boto3.client('sts')

accounts_with_errors = []

for account in account_ids:
    print('Running ' + ACTION_NAME + ' in Account: ' + account)
    account_orgs_role_arn = 'arn:aws:iam::' + \
        account + ':role/' + ORGS_ACCESS_ROLE_NAME
    try:
        if account not in [master_account_id] and account not in EXCLUDED_ACCOUNT_IDS:
            credentials = sts.assume_role(
                RoleArn=account_orgs_role_arn,
                RoleSessionName='RunInOrgScript',
            ).get('Credentials')
            for region in service_regions:
                member_session = boto3.Session(region_name=region,
                                         aws_access_key_id=credentials.get('AccessKeyId'),
                                         aws_secret_access_key=credentials.get('SecretAccessKey'),
                                         aws_session_token=credentials.get('SessionToken'),
                                         )
                member_client = member_session.client(SERVICE_NAME, region_name=region)
                print('Running in : ' + region)
                # TODO: Action is not paginated, add pagination logic
                # if action does not support pagination continue as normal
                action = getattr(member_client, ACTION_NAME)
                print(action())
        if account == master_account_id:
            # TODO: Action is not paginated, add pagination logic
            # if action does not support pagination continue as normal
            for region in service_regions:
                master_session = boto3.Session(region_name=region)
                print('Running in : ' + region)
                master_client = master_session.client(SERVICE_NAME, region_name=region)
                action = getattr(master_client, ACTION_NAME)
                print(action())
    except Exception as e:
        print(e)
        print('An error occoured in ' + account)
        accounts_with_errors.append(account)
        while continue_on_error not in ['y', 'a']:
            continue_on_error = input('Do you want to continue? Y/A/N: ')
            if continue_on_error.lower().startswith('y'):
                print("Continuing")
                continue_on_error = 'unknown'
                break
            elif continue_on_error.lower().startswith('a'):
                print("Continuing")
                continue_on_error = 'a'
            elif continue_on_error.lower().startswith('n'):
                print("Exiting")
                exit(1)
if accounts_with_errors:
    print('Accounts with Errors: ' + str(accounts_with_errors))
