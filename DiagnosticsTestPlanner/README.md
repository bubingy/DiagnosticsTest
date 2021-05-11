# DiagnosticsTestPlanner
DiagnosticsTestPlanner is part of Diagnostics Automation Test System. Its main function is getting test plan and publishing test tasks on rabbitmq.

## Requirements
schedule

## Deploy
1. Create a container with python3.6+ and required modules installed. 
2. Modify `connection.json` if necessary.
3. Run `python planner.py`.

## cli tools
In order to get test paraments quickly, you can run `python get_test_paraments.py`.  
The tool will print out os rotation, sdk version, tool version and PR info.  

Retrieving version of diagnostics tool requires authority. Once you can't get tool version any more, try following steps:
1. open https://dev.azure.com/dnceng/internal/_build?definitionId=528&_a=summary in web browser in debug mode;
2. select `network` tab;
3. choose `_build?definitionId=528&_a=summary`;
4. Copy value of `cookie` in `Request Headers`;
5. Replace value of `cookie` in `TestParaments/configuration.json` with what you copied in step 4;
6. Re-run the tool.
