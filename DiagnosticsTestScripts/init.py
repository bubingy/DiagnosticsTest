'''Install sdk and tools
'''

import os
import sys
from urllib import request

import config
from utils import run_command_sync, Result, test_logger


def prepare_test_bed():
    '''Create folders for TestBed and TestResult.
    '''
    try:
        if not os.path.exists(config.configuration.test_bed):
            os.makedirs(config.configuration.test_bed)
        if not os.path.exists(config.configuration.test_result):
            os.makedirs(config.configuration.test_result)
    except Exception as e:
        print(e)
        exit(-1)


@test_logger(os.path.join(config.configuration.test_result, f'{__name__}.log'))
def install_sdk(log_path: os.PathLike=None):
    '''Install .net(core) sdk
    '''
    sdk_dir = os.environ['DOTNET_ROOT']
    if 'win' in config.configuration.rid:
        script_url = 'https://dot.net/v1/dotnet-install.ps1'
        shell_name = 'powershell.exe'
    else:
        script_url = 'https://dotnet.microsoft.com/download/dotnet-core/scripts/v1/dotnet-install.sh'
        shell_name = '/bin/bash'

    try:
        req = request.urlopen(script_url)
        with open(f'{config.configuration.test_bed}/{os.path.basename(script_url)}', 'w+') as f:
            f.write(req.read().decode())
    except Exception as e:
        with open(log_path, 'a+') as log:
            log.write('fail to download install script!\n')
        sys.exit(-1)
    rt_code = run_command_sync(
        ' '.join(
            [
                f'{shell_name} {config.configuration.test_bed}/{os.path.basename(script_url)}',
                f'-InstallDir {sdk_dir} -v {config.configuration.sdk_version}'
            ]
        ),
        log_path=log_path
    )
    if rt_code == 0:
        return Result(0, 'successfully install sdk', None)
    else:
        with open(log_path, 'a+') as log:
            log.write('fail to install sdk!\n')
        sys.exit(-1)


@test_logger(os.path.join(config.configuration.test_result, f'{__name__}.log'))
def install_tools(log_path: os.PathLike=None):
    '''Install diagnostics
    '''
    tools = [
        'dotnet-counters',
        'dotnet-dump',
        'dotnet-gcdump',
        'dotnet-sos',
        'dotnet-trace'
    ]
    for tool in tools:
        rt_code = run_command_sync(
            ' '.join(
                [
                    f'dotnet tool install {tool}',
                    f'--tool-path {config.configuration.tool_root}',
                    f'--version {config.configuration.tool_version}',
                    f'--add-source {config.configuration.tool_feed}'
                ]
            ),
            log_path=log_path
        )
        if rt_code != 0:
            with open(log_path, 'a+') as log:
                log.write(f'fail to install tool: {tool}!\n')
            sys.exit(-1)

