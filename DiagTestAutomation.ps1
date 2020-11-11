########################################
######        Configuration       ######
########################################
$Script:RID="osx-x64"   
$Script:Debugger="lldb" 
$Script:SdkVersion="5.0.100-preview.7.20319.6"
$Script:ToolVersion="5.0.0-preview.20319.1" 
$Script:CommitID="2f9f4baebdedbf74a57c886708760b652b3e6c96"
$Script:Benchmarks="False" 
$Script:TestBed=[io.path]::combine(
    $Env:HOME, "DiagnosticsTestBed" 
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

$Script:TestResult=Join-Path $TestBed "TestResult"
if(Test-Path -Path $TestResult){ Write-Output "the output folder $TestResult already exsists" } 
else { mkdir $TestResult }

########################################
######      Install .Net SDK      ######
########################################
function InstallSDK { 
    Set-Location $TestBed
    if($RID.Contains("win")) {
        Invoke-WebRequest 'https://dot.net/v1/dotnet-install.ps1' -OutFile 'dotnet-install.ps1'
        ./dotnet-install.ps1 -i $env:DOTNET_ROOT -v $SdkVersion
    }
    if ($RID.Contains("linux") -or $RID.Contains("osx")) {
        Invoke-WebRequest "https://dotnet.microsoft.com/download/dotnet-core/scripts/v1/dotnet-install.sh" -OutFile "dotnet-install.sh"
        chmod +x dotnet-install.sh
        ./dotnet-install.sh -i $env:DOTNET_ROOT -v $SdkVersion
    }
}

########################################
######    Install diagnostics     ######
########################################
function InstallDiagnostics {
    $ToolNames = "dotnet-counters", "dotnet-dump", "dotnet-gcdump", "dotnet-sos", "dotnet-trace"
    if ($ToolVersion -ne ""){
        foreach ($ToolName in $ToolNames) {
            dotnet tool install -g $ToolName --version $ToolVersion --add-source https://pkgs.dev.azure.com/dnceng/public/_packaging/dotnet-tools/nuget/v3/index.json
        }
    } else {
        foreach ($ToolName in $ToolNames) {
            dotnet tool install -g $ToolName
        }
    }
    
}

########################################
######    run GCDumpPlayground2   ######
########################################
function RunGCDumpPlayground {
    $ProjectDir = Join-Path $WorkDir "GCDumpPlayground2"
    Set-Location $ProjectDir

    if (Test-Path (Join-Path $ProjectDir "flag")) { Remove-Item $ProjectDir/"flag" }

    $ProjectFile = Join-Path $ProjectDir "GCDumpPlayground2.csproj"
    $ProjContent = [xml](Get-Content $ProjectFile)
    $ProjContent.Project.PropertyGroup.TargetFramework = "netcoreapp" + $SdkVersion.Substring(0, 3)
    $ProjContent.Save($ProjectFile)

    dotnet build
    $Process = ""
    if ($RID.Contains("win")) {
        $BinPath = Get-Item $ProjectDir/bin/Debug/net*/GCDumpPlayground2.exe
        $Process = Start-Process -FilePath $BinPath -ArgumentList "0.1" -NoNewWindow -PassThru
    } 
    if ($RID.Contains("linux")) {
        $BinPath = Get-Item $ProjectDir/bin/Debug/net*/GCDumpPlayground2
        chmod +x $BinPath
        $Process = Start-Process -FilePath $BinPath -ArgumentList "0.1" -NoNewWindow -PassThru
    }
    if ($RID.Contains("osx")) {
        $DllPath = Get-Item $ProjectDir/bin/Debug/net*/GCDumpPlayground2.dll
        $Process = Start-Process -FilePath dotnet -ArgumentList $DllPath, "0.1" -NoNewWindow -PassThru
    }
    
    while (1) {
        if (Test-Path (Join-Path $ProjectDir "flag")) { break }
        Start-Sleep -s 1
    }
    Remove-Item -Path (Join-Path $ProjectDir "flag")

    return $Process
}

########################################
######         create webapp      ######
########################################
function CreateWebapp {
    Set-Location $TestBed
    if ([System.IO.File]::Exists("webapp")) {
        Remove-Item "webapp" -Recurse
    }
    dotnet new webapp -o webapp
}

########################################
######         run webapp         ######
########################################
function RunWebapp {
    Set-Location $TestBed
    $ProjectDir = Join-Path $TestBed "webapp"
    Set-Location $ProjectDir
    if (Test-Path (Join-Path $ProjectDir "output.txt")) { Remove-Item $ProjectDir/"output.txt" }
    
    New-Item -Path $ProjectDir -Name "output.txt"
    $OutputFile = Join-Path $ProjectDir "output.txt"

    dotnet build
    $Process = ""
    if ($RID.Contains('win')) {
        $BinPath = Get-Item $ProjectDir/bin/Debug/net*/webapp.exe
        $Process = Start-Process -FilePath $BinPath -NoNewWindow -RedirectStandardOutput $OutputFile -PassThru
    }
    if ($RID.Contains("linux")) {
        $BinPath = Get-Item $ProjectDir/bin/Debug/net*/webapp
        chmod +x $BinPath
        $Process = Start-Process -FilePath $BinPath -NoNewWindow -RedirectStandardOutput $OutputFile -PassThru
    }
    if ($RID.Contains("osx")) {
        $DllPath = Get-Item $ProjectDir/bin/Debug/net*/webapp.dll
        $Process = Start-Process -FilePath dotnet -ArgumentList $DllPath -NoNewWindow -RedirectStandardOutput $OutputFile -PassThru
    }
    
    while (1) {
        $Output = Get-Content $OutputFile | Out-String
        if ($Output.Contains("Application started")) { 
            break 
        }
        Start-Sleep -s 2
    }
    return $Process
}

########################################
######       run benchmarks       ######
########################################
function RunBenchmark {

    if ($Benchmarks -eq "False") {
        Write-Output "ignore benchmark tests"
        return
    }
    
    $ProjectRoot = Join-Path $TestBed "diagnostics"
    if ([System.IO.File]::Exists($ProjectRoot)) {
        Remove-Item $ProjectRoot -Recurse
    }

    Set-Location $TestBed
    git clone "https://github.com/dotnet/diagnostics.git"
    Set-Location $ProjectRoot
    git reset --hard $CommitID

    $ProjectDir = [io.path]::combine(
        $ProjectRoot, "src", "tests", "benchmarks"
    )

    Set-Location $ProjectDir
    $ProjectFile = [io.path]::combine(
        $ProjectDir, "benchmarks.csproj"
    )
    
    $ProjContent = [xml](Get-Content $ProjectFile)
    $ProjContent.Project.PropertyGroup.TargetFramework = "netcoreapp" + $SdkVersion.Substring(0, 3)
    $ProjContent.Save($ProjectFile)
    dotnet run -c release
    $ArtifactsDir = [io.path]::combine(
        $ProjectDir, "BenchmarkDotNet.Artifacts"
    )
    Copy-Item -Path $ArtifactsDir -Destination $TestResult -Recurse
}

########################################
######     test dotnet-counters   ######
########################################
function TestCounters { param([string]$ProcessID)
    Set-Location $TestBed
    New-Item -Path $TestResult -Name "log_dotnet-counters.txt"
    $LogPath = Join-Path $TestResult "log_dotnet-counters.txt"

    "dotnet-counters --help" | Out-File $LogPath -Append
    dotnet-counters --help | Out-File $LogPath -Append
    "dotnet-counters --version" | Out-File $LogPath -Append
    dotnet-counters --version | Out-File $LogPath -Append
    "dotnet-counters list" | Out-File $LogPath -Append
    dotnet-counters list | Out-File $LogPath -Append
    "dotnet-counters ps" | Out-File $LogPath -Append
    dotnet-counters ps | Out-File $LogPath -Append

    $Process = Start-Process dotnet-counters -ArgumentList "collect", "-p", $ProcessID -NoNewWindow -PassThru
    Start-Sleep -Seconds 10
    Stop-Process -Id $Process.Id

    $Process = Start-Process dotnet-counters -ArgumentList "monitor", "-p", $ProcessID -NoNewWindow -PassThru
    Start-Sleep -Seconds 10
    Stop-Process -Id $Process.Id
}

########################################
######       test dotnet-dump     ######
########################################
function TestDump { param([string]$ProcessID)
    if ($RID -eq "osx-x64"){
        Write-Output "dotnet-dump not support this platform"
        return
    }
    
    Set-Location $TestBed
    New-Item -Path $TestResult -Name "log_dotnet-dump.txt"
    $LogPath = Join-Path $TestResult "log_dotnet-dump.txt"

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
        Set-Location $TestBed
        $DumpPath = Get-Item $TestBed\dump*.dmp
    } 
    if ($RID.Contains("linux")) {
        Set-Location $TestBed
        $DumpPath = Get-Item $TestBed/core_*
    }
    New-Item -Path $TestResult -Name "log_dotnet-analyze.txt"
    $AnalyzeOutput = Join-Path $TestResult "log_dotnet-analyze.txt"
    $AnalyzeCommands = Join-Path $WorkDir "AnalyzeCommands.txt"
    $Process = Start-Process -FilePath dotnet-dump -ArgumentList "analyze", $DumpPath -NoNewWindow -PassThru -RedirectStandardOutput $AnalyzeOutput -RedirectStandardInput $AnalyzeCommands -Wait

    $Process.Close()
}

########################################
######     test dotnet-gcdump     ######
########################################
function TestGCDump { param([string]$ProcessID)
    Set-Location $TestResult
    New-Item -Path $TestResult -Name "log_dotnet-gcdump.txt"
    $LogPath = Join-Path $TestResult "log_dotnet-gcdump.txt"

    "dotnet-gcdump --help" | Out-File $LogPath -Append
    dotnet-gcdump --help | Out-File $LogPath -Append
    "dotnet-gcdump --version" | Out-File $LogPath -Append
    dotnet-gcdump --version | Out-File $LogPath -Append
    "dotnet-gcdump ps" | Out-File $LogPath -Append
    dotnet-gcdump ps | Out-File $LogPath -Append
    "dotnet-gcdump collect -p $ProcessID -v" | Out-File $LogPath -Append
    dotnet-gcdump collect -p $ProcessID -v | Out-File $LogPath -Append
}

########################################
######      test dotnet-sos       ######
########################################
function TestSOS { param([string]$ProcessID)
    if ($Script:RID.Contains("musl")) {
        Write-Output "dotnet-sos not support this platform"
        return
    }

    Set-Location $TestBed
    New-Item -Path $TestResult -Name "log_dotnet-sos.txt"
    $LogPath = Join-Path $TestResult "log_dotnet-sos.txt"

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
    
    New-Item -Path $TestResult -Name "log_debug-dump.txt"
    $DebugDumpOutput = Join-Path $TestResult "log_debug-dump.txt"
    New-Item -Path $TestResult -Name "log_debug-process.txt"
    $DebugProcessOutput = Join-Path $TestResult "log_debug-process.txt"

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
}

########################################
######      test dotnet-trace     ######
########################################
function TestTrace { param([string]$ProcessID)
    Set-Location $TestBed
    New-Item -Path $TestResult -Name "log_dotnet-trace.txt"
    $LogPath = Join-Path $TestResult "log_dotnet-trace.txt"

    "dotnet-trace --help" | Out-File $LogPath -Append
    dotnet-trace --help | Out-File $LogPath -Append
    "dotnet-trace --version" | Out-File $LogPath -Append
    dotnet-trace --version | Out-File $LogPath -Append
    "dotnet-trace list-profiles" | Out-File $LogPath -Append
    dotnet-trace list-profiles | Out-File $LogPath -Append
    "dotnet-trace ps" | Out-File $LogPath -Append
    dotnet-trace ps | Out-File $LogPath -Append
    
    New-Item -Path $TestBed -Name "tmp-trace.txt"
    $Process = Start-Process dotnet-trace -ArgumentList "collect", "-p", $ProcessID -NoNewWindow -PassThru -RedirectStandardOutput "tmp-trace.txt"
    Start-Sleep -Seconds 10
    Stop-Process -Id $Process.Id
    Remove-Item "tmp-trace.txt"
    
    New-Item -Path $TestBed -Name "tmp-trace.txt"
    $Process = Start-Process dotnet-trace -ArgumentList "collect", "-p", $ProcessID, "--format", "speedscope" -NoNewWindow -PassThru -RedirectStandardOutput "tmp-trace.txt"
    Start-Sleep -Seconds 10
    Stop-Process -Id $Process.Id
    Remove-Item "tmp-trace.txt"
}

function MainProcess {
    InstallSDK
    InstallDiagnostics

    RunBenchmark

    $Process = RunGCDumpPlayground
    TestGCDump($Process.Id)
    Stop-Process -Id $Process.Id

    CreateWebapp
    $Process = RunWebapp
    TestCounters($Process.Id)
    TestDump($Process.Id)
    TestSOS($Process.Id)
    TestTrace($Process.Id)
    Stop-Process -Id $Process.Id 
}

MainProcess
