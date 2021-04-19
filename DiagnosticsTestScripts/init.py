'''Install sdk and tools
'''

import os
import sys
from urllib import request

from config import configuration
from utils import run_command_sync, Result


log_path = os.path.join(configuration.test_result, 'init.log')


def prepare_test_bed():
    '''Create folders for TestBed and TestResult.
    '''
    try:
        if not os.path.exists(configuration.test_bed):
            os.makedirs(configuration.test_bed)
        if not os.path.exists(configuration.test_result):
            os.makedirs(configuration.test_result)
    except Exception as e:
        print(e)
        exit(-1)


def install_sdk():
    '''Install .net(core) sdk
    '''
    sdk_dir = os.environ['DOTNET_ROOT']
    if 'win' in configuration.rid:
        script_url = 'https://dot.net/v1/dotnet-install.ps1'
        shell_name = 'powershell.exe'
    else:
        script_url = 'https://dotnet.microsoft.com/download/dotnet-core/scripts/v1/dotnet-install.sh'
        shell_name = '/bin/bash'

    try:
        req = request.urlopen(script_url)
        with open(f'{configuration.test_bed}/{os.path.basename(script_url)}', 'w+') as f:
            f.write(req.read().decode())
    except Exception as e:
        with open(log_path, 'a+') as log:
            log.write('fail to download install script!\n')
        sys.exit(-1)
    rt_code = run_command_sync(
        ' '.join(
            [
                f'{shell_name} {configuration.test_bed}/{os.path.basename(script_url)}',
                f'-i {sdk_dir} -v {configuration.sdk_version}'
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


def install_tools():
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
                    f'dotnet tool install -g {tool}',
                    f'--version {configuration.tool_version}',
                    f'--add-source {configuration.tool_feed}'
                ]
            ),
            log_path=log_path
        )
        if rt_code != 0:
            with open(log_path, 'a+') as log:
                log.write(f'fail to install tool: {tool}!\n')
            sys.exit(-1)
