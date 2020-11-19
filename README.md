# DiagnosticsTestTools
Automation scripts for diagnostics tools test.

## Requirements
* python3.6 or later

## Usage
### Step 1
Before running these scripts, please make sure delete following files and directory:
* the directory where you install the sdk, in our case, this directory is named `.dotnet-test`;
* the directory where you install the tools, in our case, this directory is in the home directory whose name is `.dotnet`;
* lldb init file and configuration directory, generally, just delete `.lldbinit` and `.lldb` in the home directory;
### Step 2
Set environment variables:
1. DOTNET_ROOT: where to install sdk;
2. PATH: append some directory so that the system could find specified files.  
### Step 3
Configure run Options. Please see `config.conf` for more details.
### Step 4
Run `python3/python.exe run_test.py`
