# DiagnosticsTestPlanner
DiagnosticsTestPlanner is part of Diagnostics Automation Test System. Its main function is getting test plan and publishing test tasks on rabbitmq.

## Requirements
pika
schedule

## Deploy
1. Create a container with python3.6+ and required modules installed. 
2. Modify `connection.json` if necessary.
3. Run `python planner.py`.