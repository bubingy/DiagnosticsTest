'''Install .NET SDK'''

import os
from urllib import request

from services.terminal import run_command_sync, PIPE
from instances.logger import ScriptLogger


def install_sdk_from_script(sdk_version: str, 
                            test_bed: os.PathLike,
                            dotnet_root: os.PathLike,
                            rid: str,
                            arch: str=None,
                            logger: ScriptLogger=None) -> None:
    logger.info(f'download dotnet install script')
    
    if 'win' in rid:
        script_download_link = 'https://dot.net/v1/dotnet-install.ps1'
        script_engine = 'powershell.exe'

    else:
        script_download_link = 'https://dotnet.microsoft.com/download/dotnet/scripts/v1/dotnet-install.sh'
        script_engine = '/bin/bash'

    script_path = os.path.join(test_bed, os.path.basename(script_download_link))
    req = request.urlopen(script_download_link)
    with open(script_path, 'w+') as f:
        f.write(req.read().decode())

    if 'win' not in rid:
        run_command_sync(f'chmod +x {script_path}')

    if arch is not None:
        command = f'{script_engine} {script_path} -InstallDir {dotnet_root} -v {sdk_version} -Architecture {arch}'
    else:
        command = f'{script_engine} {script_path} -InstallDir {dotnet_root} -v {sdk_version}'
    
    outs, errs = run_command_sync(command, stdout=PIPE, stderr=PIPE)
    logger.info(f'run command:\n{command}\n{outs}')
    
    if errs != '':
        logger.error(f'fail to install .net SDK {sdk_version}!\n{errs}')
        exit(-1)


def install_runtime_from_script(runtime_version: str, test_bed: os.PathLike, rid: str, logger: ScriptLogger):
    logger.info(f'download dotnet install script')
    dotnet_root = os.environ['DOTNET_ROOT']
    if 'win' in rid:
        script_download_link = 'https://dot.net/v1/dotnet-install.ps1'
        script_engine = 'powershell.exe'

    else:
        script_download_link = 'https://dotnet.microsoft.com/download/dotnet/scripts/v1/dotnet-install.sh'
        script_engine = '/bin/bash'

    script_path = os.path.join(test_bed, os.path.basename(script_download_link))
    req = request.urlopen(script_download_link)
    with open(script_path, 'w+') as f:
        f.write(req.read().decode())

    if 'win' not in rid:
        run_command_sync(f'chmod +x {script_path}')

    command = f'{script_engine} {script_path} -InstallDir {dotnet_root} -v {runtime_version} --runtime dotnet'
    outs, errs = run_command_sync(command, stdout=PIPE, stderr=PIPE)
    logger.info(f'run command:\n{command}\n{outs}')
    
    if errs != '':
        logger.error(f'fail to install .net runtime {runtime_version}!\n{errs}')
        exit(-1)

