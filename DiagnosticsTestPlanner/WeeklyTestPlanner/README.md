# WeeklyTestPlanner
WeeklyTestPlanner is used to get weekly test plan and publishing test tasks on rabbitmq.

## Requirements
schedule

## Deploy
1. Create a container with python3.6+ and required modules installed. 
2. Modify `rabbitmq.ini` if necessary.
3. Run
```
python weekly_test_planner.py
```

## cli tools
In order to get test paraments of this week quickly, you can run 
```
python get_test_paraments.py --output /path/to/testplan.xlsx
```
The tool will print out os rotation, sdk version, tool version and PR info.  

Retrieving version of diagnostics tool requires additional authority. Once you can't get tool version any more, you may need to refresh you PAT(personal access tokens). Please go through the [document](https://docs.microsoft.com/en-us/azure/devops/organizations/accounts/use-personal-access-tokens-to-authenticate?view=azure-devops&tabs=preview-page) for details.

