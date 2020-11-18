# Introduction
These scripts are used to run diagnostics test.
More details about diagnostics are available in [dotnet diagnostics](https://github.com/dotnet/diagnostics).<br/>

# Preparation
## Windows 10
* Install packages needed by [diagnostics](https://github.com/dotnet/diagnostics/blob/master/documentation/building/windows-instructions.md).
* Install Windows SDK with debugger, so that we can use cdb in the test.
* Add Environment variables and active them.
## OSX 10.14
* Install packages needed by [diagnostics](https://github.com/dotnet/diagnostics/blob/master/documentation/building/osx-instructions.md).
* Login as the root. Add Environment variables and active them. Remember to run command 'source ~/.bashrc' each time you create a session.
* Install powershell.
## Linux(container, VM)
* Install packages needed by [diagnostics](https://github.com/dotnet/diagnostics/blob/master/documentation/building/linux-instructions.md).
* Login as the root. Add Environment variables and active them.
* Install powershell.

# Configure
Open up `DiagTestAutomation.ps1`, you will see Configuration section at the beginning. You need to configure some paraments before running this script.
* $Script:RID: RID is short for [Runtime Identifier](https://docs.microsoft.com/en-us/dotnet/core/rid-catalog). The value of $Script:RID depends on the platform where you decide to run this script.
* $Script:Debugger: Alias of the native debugger. This variable goes into effect only on OSX and Linux.
* $Script:SdkVersion: Version of [.Net core SDK](https://github.com/dotnet/installer).
* $Script:ToolVersion: Version of [diagnostics tool](https://dev.azure.com/dnceng/internal/_build?definitionId=528&_a=summary).
* $Script:CommitID: [Commit ID](https://github.com/dotnet/diagnostics/commits/master). It depends on ToolVersion.
* $Script:Benchmarks: Whether to run Benchmarks test, use 'True' or 'False'.
* $Script:TestBed: The directory used to store test result and temp file. Please use absolute path.

If you want run this scripts on windows, also modify `DebugCommands-win.txt`. Replace the alias in line 2 with the user name of the current session.

# Run scirpt
On linux and OSX, make sure you run this script as the root.
