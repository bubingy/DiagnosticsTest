# DiagnosticsTestPlanner
Diagnostics WeeklyTestPlanner is part of Diagnostics Automation Test System. It contains 2 independent components: WeeklyTestPlanner and ReleaseTestPlanner.  

## Requirements
schedule  
openpyxl 

## Preparation
1. modify `conf/rabbitmq.ini` if necessary.
2. Retrieving version of diagnostics tool requires additional authority. Once you can't get tool version any more, you may need to refresh you PAT(personal access tokens). Please go through the [document](https://docs.microsoft.com/en-us/azure/devops/organizations/accounts/use-personal-access-tokens-to-authenticate?view=azure-devops&tabs=preview-page) for details.

## Usage
1. print test plan in console and write it into a xlsx file:
```
python print_test_plan.py --output <path of xlsx file> --type <release|weekly>
```

2. publish test plans to rabbitmq:
```
python publish_test_plan.py --type <release|weekly>
```