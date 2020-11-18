########################################
######        Configuration       ######
########################################
$Script:SdkVersion="5.0.100-preview.7.20319.6"
$Script:NetTrace=[io.path]::combine(
    $Env:HOME, "NetTrace" 
)

########################################
######       Initialization       ######
########################################
if ($Env:HOME -ne "/root") {
    Write-Output "Please run this script with root"
    Exit(-1)
}

$Script:WorkDir=Split-Path -Parent $MyInvocation.MyCommand.Definition
if(Test-Path -Path $NetTrace) { Write-Output "the work folder $WorkDir already exsists" }
else { mkdir $TestBed }

########################################
######      Install .Net SDK      ######
########################################
function InstallSDK { 
    Set-Location $TestBed
    Invoke-WebRequest "https://dotnet.microsoft.com/download/dotnet-core/scripts/v1/dotnet-install.sh" -OutFile "dotnet-install.sh"
    chmod +x dotnet-install.sh
    ./dotnet-install.sh -i $env:DOTNET_ROOT -v $SdkVersion
}

########################################
######       Remove .Net SDK      ######
########################################
function RemoveSDK { 
    Set-Location $Env:HOME
    Remove-Item -Recurse .dotnet .dotnet-test .aspnet .nuget .templateengine
}

########################################
######    Download perfcollect    ######
########################################
function DownloadPerfcollect {
    Set-Location $NetTrace
    Invoke-WebRequest 'http://aka.ms/perfcollect' -OutFile 'perfcollect'
    chmod +x perfcollect
}

########################################
######       Run gcperfsim        ######
########################################
function RunGcperfsim {
    $ProjectDir = Join-Path $WorkDir "gcperfsim"
    Set-Location $ProjectDir

    $ProjectFile = Join-Path $ProjectDir "gcperfsim.csproj"
    $ProjContent = [xml](Get-Content $ProjectFile)
    $ProjContent.Project.PropertyGroup.TargetFramework = "netcoreapp" + $SdkVersion.Substring(0, 3)
    $ProjContent.Save($ProjectFile)

    $Env:COMPlus_PerfMapEnabled=0
    $Env:COMPlus_EnableEventLog=0
    try {
        dotnet build
    }
    catch {
        Write-Output "fail to build gcperfsim"
        Exit(-1)
    }
    $BinPath = Get-Item $ProjectDir/bin/Debug/net*/gcperfsim
    $Env:COMPlus_PerfMapEnabled=1
    $Env:COMPlus_EnableEventLog=1
    $Process = Start-Process -FilePath $BinPath -NoNewWindow -PassThru

    return $Process
}

function CollectTrace { param($Process)
    Set-Location $NetTrace
    ./perfcollect collect netcore$SdkVersion.Substring(0, 3) -collectsec 30
}