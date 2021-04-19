'''Install sdk and tools
'''

import os
from urllib import request

from config import configuration
from utils import run_command_sync, Result


log_path = os.path.join(configuration.test_bed, 'init.log')


def prepare_test_bed():
    '''Create folders for TestBed.
    '''
    try:
        if not os.path.exists(configuration.test_bed):
            os.makedirs(configuration.test_bed)
        if not os.path.exists(configuration.dump_directory):
            os.makedirs(configuration.dump_directory)
        if not os.path.exists(configuration.analyze_output):
            os.makedirs(configuration.analyze_output)
    except Exception as e:
        print(e)
        exit(-1)


def install_sdk(arch: str='x64'):
    '''Install .net(core) sdk
    '''
    sdk_dir = os.environ['DOTNET_ROOT']
    if 'win' in configuration.rid:
        req = request.urlopen('https://dot.net/v1/dotnet-install.ps1')
        with open(f'{configuration.test_bed}/dotnet-install.ps1', 'w+') as f:
            f.write(req.read().decode())
        rt_code = run_command_sync(
            ' '.join(
                [
                    f'powershell.exe {configuration.test_bed}/dotnet-install.ps1',
                    f'-i {sdk_dir} -v {configuration.sdk_version} --architecture {arch}'
                ]
            ),
            log_path=log_path
        )
    else:
        req = request.urlopen(
            'https://dotnet.microsoft.com/download/dotnet-core/scripts/v1/dotnet-install.sh'
        )
        with open(f'{configuration.test_bed}/dotnet-install.sh', 'w+') as f:
            f.write(req.read().decode())
        run_command_sync(f'chmod +x {configuration.test_bed}/dotnet-install.sh')
        if configuration.rid == 'linux-musl-arm64':
            rt_code = run_command_sync(
                (
                    f'/bin/bash {configuration.test_bed}/dotnet-install.sh '
                    f'-v {configuration.runtime_version} --runtime dotnet'
                ),
                log_path=log_path
            )
        else:
            rt_code = run_command_sync(
                ' '.join(
                    [
                        f'/bin/bash {configuration.test_bed}/dotnet-install.sh',
                        f'-i {sdk_dir} -v {configuration.sdk_version}'
                    ]
                ),
                log_path=log_path
            )
    if rt_code == 0:
        return Result(0, 'successfully install sdk', None)
    else:
        return Result(rt_code, 'fail to install sdk', None)


def install_tools():
    '''Install diagnostics
    '''
    run_command_sync(
        (
            'dotnet tool install -g dotnet-dump '
            f'--version {configuration.tool_version} '
            f'--add-source {configuration.tool_feed}'
        ),
        log_path=log_path
    )
