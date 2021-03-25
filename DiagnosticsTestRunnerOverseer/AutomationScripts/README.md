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

## Other tools
### getTestParaments
In order to get test paraments quickly, we develop `getTestParaments` in `tools` directory.  
Run following command on windows:
```
cd tools/getTestParaments
python get_test_paraments.py
```
The tool will print out sdk version, tool version and PR info.  

Retrieving version of diagnostics tool requires authority. Once you can't get tool version any more, try following steps:
1. open https://dev.azure.com/dnceng/internal/_build?definitionId=528&_a=summary in web browser in debug mode;
2. select `network` tab;
3. choose `_build?definitionId=528&_a=summary`;
4. Copy value of `cookie` in `Request Headers`;
5. Replace value of `cookie` in `tools/getTestParaments/configuration.py` with what you copied in step 4;
6. Re-run the tool.
