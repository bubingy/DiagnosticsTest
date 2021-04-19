# DiagnosticsTestTools
Automation scripts for diagnostics tools test.

## Requirements
* python3.6 or later;
* lldb on Linux and OSX, CDB on Windows. (make lldb available in `/usr/bin`);

## Usage
### Step 1
Before running these scripts, Run `python3/python.exe clean.py`;
### Step 2
Configure run Options. Please see `config.conf` for more details.
### Step 3
Run `python3/python.exe run_test.py`.