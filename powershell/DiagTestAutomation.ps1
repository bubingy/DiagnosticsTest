########################################
######        Configuration       ######
########################################
$Script:RID="win-x64"   
$Script:Debugger="cdb" 
$Script:SdkVersion="5.0.100-rtm.20515.8"
$Script:ToolVersion="5.0.0-preview.20559.1" 
$Script:CommitID="93278f1e5b30162ea8afbd66fb20e6e7bd3bbdef"
$Script:Benchmarks="False" 
$Script:TestBed=[io.path]::combine(
    "F:\Workspace\.NET-Diagnostics\", "DiagnosticsTestBed" 
)
<# Here is an example on OSX:
$Script:RID="osx-x64"   
$Script:Debugger="lldb" 
$Script:SdkVersion="5.0.100-preview.7.20319.6"
$Script:ToolVersion="5.0.0-preview.20319.1" 
$Script:CommitID="2f9f4baebdedbf74a57c886708760b652b3e6c96"
$Script:Benchmarks="False" 
$Script:TestBed=[io.path]::combine(
    $Env:HOME, "DiagnosticsTestBed" 
)
#>

########################################
######       Initialization       ######
########################################
$Script:WorkDir=Split-Path -Parent $MyInvocation.MyCommand.Definition
if(Test-Path -Path $TestBed) { Write-Output "the work folder $WorkDir already exsists" }
else { mkdir $TestBed }

$Script:TestResult=[io.path]::combine($TestBed, "TestResult")
if(Test-Path -Path $TestResult){ Write-Output "the output folder $TestResult already exsists" } 
else { mkdir $TestResult }

$Script:BinExtend=""
if ($RID.Contains("win")) {
    $BinExtend=".exe"
}
########################################
######      Install .Net SDK      ######
########################################
function InstallSDK { 
    Push-Location $TestBed
    if($RID.Contains("win")) {
        Invoke-WebRequest 'https://dot.net/v1/dotnet-install.ps1' -OutFile 'dotnet-install.ps1'
        ./dotnet-install.ps1 -i $env:DOTNET_ROOT -v $SdkVersion
    }
    if ($RID.Contains("linux") -or $RID.Contains("osx")) {
        Invoke-WebRequest "https://dotnet.microsoft.com/download/dotnet-core/scripts/v1/dotnet-install.sh" -OutFile "dotnet-install.sh"
        chmod +x dotnet-install.sh
        ./dotnet-install.sh -i $env:DOTNET_ROOT -v $SdkVersion
    }
    Pop-Location
}

########################################
######    Install diagnostics     ######
########################################
function InstallDiagnostics {
    $ToolNames = "dotnet-counters", "dotnet-dump", "dotnet-gcdump", "dotnet-sos", "dotnet-trace"
    $feed = "https://pkgs.dev.azure.com/dnceng/public/_packaging/dotnet-tools/nuget/v3/index.json"
    if ($ToolVersion -ne ""){
        foreach ($ToolName in $ToolNames) {
            dotnet tool install -g $ToolName --version $ToolVersion --add-source $feed
        }
    } else {
        foreach ($ToolName in $ToolNames) {
            dotnet tool install -g $ToolName
        }
    }
}

########################################
######  create GCDumpPlayground2  ######
########################################
function CreateGCDumpPlayground {
    $ProjectDir = [io.path]::combine($TestBed, "GCDumpPlayground2")
    if ([System.IO.File]::Exists($ProjectDir)) {
        Remove-Item $ProjectDir -Recurse
    }
    $TmpProjectDir = [io.path]::combine($TestBed, "Projects", "GCDumpPlayground2") 
    Copy-Item -Recurse $TmpProjectDir -Destination $TestBed

    $ProjectFile = [io.path]::Combine($ProjectDir, "GCDumpPlayground2.csproj")
    $ProjContent = [xml](Get-Content $ProjectFile)
    if ($SdkVersion.Substring(0, 1) -eq "3") {
        $ProjContent.Project.PropertyGroup.TargetFramework = "netcoreapp" + $SdkVersion.Substring(0, 3)
    } else {
        $ProjContent.Project.PropertyGroup.TargetFramework = "net" + $SdkVersion.Substring(0, 3)
    }
    $ProjContent.Save($ProjectFile)
    Push-Location $ProjectDir
    dotnet publish -r $RID -o $ProjectDir/out
    Pop-Location
}

########################################
######    run GCDumpPlayground2   ######
########################################
function RunGCDumpPlayground {
    $ProjectDir = [io.path]::Combine($TestBed, "GCDumpPlayground2")
    $FlagPath = [io.path]::Combine($ProjectDir, "tmp.txt")
    if (Test-Path $FlagPath) { Remove-Item $FlagPath }

    $BinPath = Get-Item $ProjectDir/out/GCDumpPlayground2$BinExtend
    $Process = Start-Process -FilePath $BinPath -ArgumentList "0.1" -NoNewWindow -PassThru -RedirectStandardOutput $FlagPath
    
    while (1) {
        $Content = Get-Content -Path $FlagPath -Raw
        if ($null -ne $Content) {
            if ($Content.Contains("Pause for gcdumps.")) { break }
        }
        Start-Sleep -s 2
    }
    return $Process
}

########################################
######         create webapp      ######
########################################
function CreateWebapp {
    $ProjectDir = [io.path]::Combine($TestBed, "webapp")
    if ([System.IO.File]::Exists($ProjectDir)) {
        Remove-Item $ProjectDir -Recurse
    }
    Push-Location $TestBed
    dotnet new webapp -o $ProjectDir
    Pop-Location
    Push-Location $ProjectDir
    dotnet build -r $RID -o out
    Pop-Location
}

########################################
######         run webapp         ######
########################################
function RunWebapp {
    $ProjectDir = [io.path]::Combine($TestBed, "webapp")
    $FlagPath = [io.path]::Combine($ProjectDir, "tmp.txt")
    if (Test-Path -Path $FlagPath) { Remove-Item -Path $FlagPath }
    
    $BinPath = Get-Item $ProjectDir/out/webapp$BinExtend
    $Process = Start-Process -FilePath $BinPath -NoNewWindow -RedirectStandardOutput $FlagPath -PassThru
    
    while (1) {
        $Content = Get-Content -Path $FlagPath -Raw
        if ($null -ne $Content) {
            if ($Content.Contains("Application started")) { break }
        }
        Start-Sleep -s 2
    }
    return $Process
}

########################################
######     create consoleapp      ######
########################################
function CreateBuildConsoleapp {
    $ProjectDir = [io.path]::Combine($TestBed, "consoleapp")
    if ([System.IO.File]::Exists($ProjectDir)) {
        Remove-Item $ProjectDir -Recurse
    }

    Push-Location $TestBed
    dotnet new console -o consoleapp
    Pop-Location
    Copy-Item $WorkDir/Projects/ConsoleAppTemp -Destination $ProjectDir/Program.cs
    Push-Location $ProjectDir
    dotnet build -r $RID -o out
    Pop-Location
}

########################################
######       run benchmarks       ######
########################################
function RunBenchmark {
    if ($Benchmarks -eq "False") {
        Write-Output "ignore benchmark tests"
        return
    }
    
    $ProjectRoot = [io.path]::combine($TestBed, "diagnostics")
    if ([System.IO.File]::Exists($ProjectRoot)) {
        Remove-Item $ProjectRoot -Recurse
    }

    Push-Location $TestBed
    git clone "https://github.com/dotnet/diagnostics.git"
    Pop-Location
    Push-Location $ProjectRoot
    git reset --hard $CommitID
    Pop-Location

    $ProjectDir = [io.path]::combine(
        $ProjectRoot, "src", "tests", "benchmarks"
    )

    $ProjectFile = [io.path]::combine(
        $ProjectDir, "benchmarks.csproj"
    )
    $ProjContent = [xml](Get-Content $ProjectFile)
    $ProjContent.Project.PropertyGroup.TargetFramework = "netcoreapp" + $SdkVersion.Substring(0, 3)
    $ProjContent.Save($ProjectFile)
    Push-Location $ProjectDir
    dotnet run -c release
    Pop-Location
    $ArtifactsDir = [io.path]::combine(
        $ProjectDir, "BenchmarkDotNet.Artifacts"
    )
    Copy-Item -Path $ArtifactsDir -Destination $TestResult -Recurse
}

########################################
######     test dotnet-counters   ######
########################################
function TestCounters {
    $LogPath = [io.path]::Combine($TestResult, "dotnet-counters.log")
    if (Test-Path -Path $LogPath) { Remove-Item -Path $LogPath }
    New-Item -Path $TestResult -Name "dotnet-counters.log"
    
    $WebappProcess = RunWebapp

    Push-Location $TestResult
    "dotnet-counters --help" | Out-File $LogPath -Append
    dotnet-counters --help | Out-File $LogPath -Append
    "dotnet-counters --version" | Out-File $LogPath -Append
    dotnet-counters --version | Out-File $LogPath -Append
    "dotnet-counters list" | Out-File $LogPath -Append
    dotnet-counters list | Out-File $LogPath -Append
    "dotnet-counters ps" | Out-File $LogPath -Append
    dotnet-counters ps | Out-File $LogPath -Append

    $Process = Start-Process dotnet-counters -ArgumentList "collect", "-p", $WebappProcess.Id -NoNewWindow -PassThru
    Start-Sleep -Seconds 10
    Stop-Process -Id $Process.Id

    $Process = Start-Process dotnet-counters -ArgumentList "monitor", "-p", $WebappProcess.Id -PassThru -NoNewWindow
    Start-Sleep -Seconds 10
    Stop-Process -Id $Process.Id

    Stop-Process -Id $WebappProcess.Id 

    if ($SdkVersion.Substring(0, 1) -eq "3") {
        write-host ".net core 3.1 doesn't support new feature of dotnet-counters"
        Pop-Location
        return
    }
    $BinPath = [io.path]::Combine($TestBed, "consoleapp", "out", "consoleapp$BinExtend")
    "dotnet-counters monitor -- $TestBed/consoleapp/out/consoleapp$BinExtend"
    dotnet-counters monitor -- $BinPath
    Pop-Location
}

########################################
######       test dotnet-dump     ######
########################################
function TestDump { param([string]$ProcessID)
    if ($RID -eq "osx-x64"){
        Write-Output "dotnet-dump not support this platform"
        return
    }
    $LogPath = [io.path]::Combine($TestResult, "dotnet-dump.log")
    if (Test-Path -Path $LogPath) { Remove-Item -Path $LogPath }
    New-Item -Path $TestResult -Name "dotnet-dump.log"

    $WebappProcess = RunWebapp

    "dotnet-dump --help" | Out-File $LogPath -Append
    dotnet-dump --help | Out-File $LogPath -Append
    "dotnet-dump --version" | Out-File $LogPath -Append
    dotnet-dump --version | Out-File $LogPath -Append
    "dotnet-dump ps" | Out-File $LogPath -Append
    dotnet-dump ps | Out-File $LogPath -Append
    "dotnet-dump collect -p $ProcessID" | Out-File $LogPath -Append
    dotnet-dump collect -p $ProcessID | Out-File $LogPath -Append
    $DumpPath = ""
    if($RID.Contains("win")) {
        $DumpPath = Get-Item $TestBed\dump*.dmp
    } 
    if ($RID.Contains("linux")) {
        $DumpPath = Get-Item $TestBed/core_*
    }
    
    $AnalyzeOutput = [io.path]::Combine($TestResult, "dotnet-analyze.log")
    if (Test-Path -Path $AnalyzeOutput) { Remove-Item -Path $AnalyzeOutput }
    New-Item -Path $TestResult -Name "dotnet-analyze.log"
    
    $AnalyzeCommands = [io.path]::Combine($WorkDir, "AnalyzeCommands.txt")
    $Process = Start-Process -FilePath dotnet-dump -ArgumentList "analyze", $DumpPath -NoNewWindow -PassThru -RedirectStandardOutput $AnalyzeOutput -RedirectStandardInput $AnalyzeCommands -Wait

    $Process.Close()
    Stop-Process -Id $WebappProcess.Id 
}

########################################
######     test dotnet-gcdump     ######
########################################
function TestGCDump {
    $LogPath = [io.path]::Combine($TestResult, "dotnet-gcdump.log")
    if (Test-Path -Path $LogPath) { Remove-Item -Path $LogPath }
    New-Item -Path $TestResult -Name "dotnet-gcdump.log"

    $Process = RunGCDumpPlayground
    $ProcessID = $Process.Id
    
    "dotnet-gcdump --help" | Out-File $LogPath -Append
    dotnet-gcdump --help | Out-File $LogPath -Append
    "dotnet-gcdump --version" | Out-File $LogPath -Append
    dotnet-gcdump --version | Out-File $LogPath -Append
    "dotnet-gcdump ps" | Out-File $LogPath -Append
    dotnet-gcdump ps | Out-File $LogPath -Append
    "dotnet-gcdump collect -p $ProcessID -v" | Out-File $LogPath -Append
    dotnet-gcdump collect -p $ProcessID -v | Out-File $LogPath -Append

    Stop-Process -Id $ProcessID
}

########################################
######      test dotnet-sos       ######
########################################
function TestSOS {
    if ($Script:RID.Contains("musl")) {
        Write-Output "dotnet-sos isn't supported on Alpine."
        return
    }

    $LogPath = [io.path]::Combine($TestResult, "dotnet-sos.log")
    if (Test-Path -Path $LogPath) { Remove-Item -Path $LogPath }
    New-Item -Path $TestResult -Name "dotnet-gcdump.log"

    "dotnet-sos --help" | Out-File $LogPath -Append
    dotnet-sos --help | Out-File $LogPath -Append
    "dotnet-sos --version" | Out-File $LogPath -Append
    dotnet-sos --version | Out-File $LogPath -Append
    "dotnet-sos install" | Out-File $LogPath -Append
    dotnet-sos install | Out-File $LogPath -Append
    "dotnet-sos uninstall" | Out-File $LogPath -Append
    dotnet-sos uninstall | Out-File $LogPath -Append
    "dotnet-sos install" | Out-File $LogPath -Append
    dotnet-sos install | Out-File $LogPath -Append

    $DumpPath = ""
    if($RID.Contains("win")) {
        $DumpPath = Get-Item $TestBed\dump*.dmp
    } elseif ($RID.Contains("linux")) {
        $DumpPath = Get-Item $TestBed/core_*
    }
    
    $DebugDumpOutput = [io.path]::Combine($TestResult, "debug-dump.log")
    if (Test-Path -Path $DebugDumpOutput) { Remove-Item -Path $DebugDumpOutput }
    New-Item -Path $TestResult -Name "debug-dump.log"
    $DebugProcessOutput = [io.path]::Combine($TestResult, "debug-process.log")
    if (Test-Path -Path $DebugProcessOutput) { Remove-Item -Path $DebugProcessOutput }
    New-Item -Path $TestResult -Name "debug-process.log"
    
    $WebappProcess = RunWebapp

    $DebugCommands = ""

    if ($RID.Contains("win")) {
        $DebugCommands = Join-Path $WorkDir "DebugCommands-win.txt"
        Write-Output "debug process ..."
        cdb -p $ProcessID -c "$<$DebugCommands" > $DebugProcessOutput
        Write-Output "debug dump ..."
        cdb -z $DumpPath  -c "$<$DebugCommands" > $DebugDumpOutput
    }

    if ($RID.Contains("linux")) {
        $DebugCommands = Join-Path $WorkDir "DebugCommands-unix.txt"
        Start-Process -FilePath $Debugger -ArgumentList "-c", $DumpPath -NoNewWindow -RedirectStandardOutput $DebugDumpOutput -RedirectStandardInput $DebugCommands -Wait
        Start-Process -FilePath $Debugger -ArgumentList "-p", $ProcessID -NoNewWindow -RedirectStandardOutput $DebugProcessOutput -RedirectStandardInput $DebugCommands -Wait 
    }

    if ($RID.Contains("osx")) {
        $DebugCommands = Join-Path $WorkDir "DebugCommands-unix.txt"
        Start-Process -FilePath $Debugger -ArgumentList "-p", $ProcessID -NoNewWindow -RedirectStandardOutput $DebugProcessOutput -RedirectStandardInput $DebugCommands -Wait
        Remove-Item $DebugDumpOutput
    }
    Stop-Process -Id $WebappProcess.Id
}

########################################
######      test dotnet-trace     ######
########################################
function TestTrace {
    $LogPath = [io.path]::Combine($TestResult, "dotnet-trace.log")
    if (Test-Path -Path $LogPath) { Remove-Item -Path $LogPath }
    New-Item -Path $TestResult -Name "dotnet-trace.log"

    $WebappProcess = RunWebapp

    "dotnet-trace --help" | Out-File $LogPath -Append
    dotnet-trace --help | Out-File $LogPath -Append
    "dotnet-trace --version" | Out-File $LogPath -Append
    dotnet-trace --version | Out-File $LogPath -Append
    "dotnet-trace list-profiles" | Out-File $LogPath -Append
    dotnet-trace list-profiles | Out-File $LogPath -Append
    "dotnet-trace ps" | Out-File $LogPath -Append
    dotnet-trace ps | Out-File $LogPath -Append
    
    Push-Location $TestBed
    $Process = Start-Process dotnet-trace -ArgumentList "collect", "-p", $ProcessID, "-o", "webapp.nettrace" -NoNewWindow -PassThru
    Start-Sleep -Seconds 20
    Stop-Process -Id $Process.Id
    Remove-Item "tmp-trace.txt"
    
    "dotnet-trace convert --format speedscope webapp.nettrace" | Out-File $LogPath -Append
    dotnet-trace convert --format speedscope webapp.nettrace | Out-File $LogPath -Append
    Pop-Location
    Stop-Process -Id $WebappProcess.Id

    if ($SdkVersion.Substring(0, 1) -eq "3") {
        write-host ".net core 3.1 doesn't support new feature of dotnet-trace"
        return
    }
    dotnet-trace collect --providers Microsoft-Windows-DotNETRuntime -- $TestBed/consoleapp/out/consoleapp$BinExtend
   
    
}

function MainProcess {
    InstallSDK
    InstallDiagnostics

    RunBenchmark

    CreateWebapp
    CreateBuildConsoleapp
    CreateGCDumpPlayground

    TestCounters
    # TestDump
    # TestGCDump
    # TestSOS
    # TestTrace
}

MainProcess
