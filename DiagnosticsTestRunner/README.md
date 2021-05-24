# DiagnosticsTestRunner

## Introduce
This script will query rabbitmq every 30 seconds. If there are tasks in the queue, the script will retrieve them and run in the backgroud.

## Usage
1. before deploying, please modify `rabbitmq.ini` and `runner.ini`.
2. run this script in the background.  
On windows:
```
Start-Job  { python \path\to\DiagnosticsTestRunner\runner.py --output \path\to\output_directory }
```
On Linux and Mac:
```
nohup python3 \path\to\DiagnosticsTestRunner\runner.py --output \path\to\output_directory &
```