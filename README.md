# aws-orgs-runner
Run an API call across all of your AWS Organization's Accounts

 The purpose of this module is to run a specific API Call
 that does not require any arguments in every Organizations
 Member Account across all supported Regions.
 Note: you must run this script in an Organizations Master Account

 Each Member Account must have an OrganizationAccountAccessRole
 or other Role in each Member Account that trusts the IAM Entity running this script
 to assume that Role. The Member Account's Role names must match the string
 provided to the variable ORGS_ACCESS_ROLE_NAME. The OrganizationAccountAccessRole 
 must have the proper IAM permissions to run the Action in ACTION_NAME

 TODO: break out into Pthon Class/Module installable via PyPi
 and include CLI interface in scripts.
 TODO: Do the same for https://github.com/walkerk1980/AWSCredsProfileManager and integrate
 the ability to create .aws/config profiles for all of the Accounts in an Org automatically.
