'''Install sdk and tools
'''

import os
import stat
from urllib import request

from config import configuration
from utils import run_command_sync, Result


log_path = os.path.join(configuration.test_result, 'init.log')


def install_sdk():
    '''Install .net(core) sdk
    '''
    sdk_dir = os.environ['DOTNET_ROOT']
    if 'win' in configuration.rid:
        req = request.urlopen('https://dot.net/v1/dotnet-install.ps1')
        with open(f'{configuration.test_bed}/dotnet-install.ps1', 'w+') as f:
            f.write(req.read().decode())
        os.chmod(f'{configuration.test_bed}/dotnet-install.ps1', stat.S_IRWXO)
        rt_code = run_command_sync(
            f'powershell.exe {configuration.test_bed}/dotnet-install.ps1 ' + \
                f'-i {sdk_dir} -v {configuration.sdk_version}',
            log_path=log_path
        )
    else:
        req = request.urlopen('https://dotnet.microsoft.com/download/dotnet-core/scripts/v1/dotnet-install.sh')
        with open(f'{configuration.test_bed}/dotnet-install.sh', 'w+') as f:
            f.write(req.read().decode())
        os.chmod(f'{configuration.test_bed}/dotnet-install.sh', stat.S_IRWXO)
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
    tools = [
        'dotnet-counters',
        'dotnet-dump',
        'dotnet-gcdump',
        'dotnet-sos',
        'dotnet-trace'
    ]
    for tool in tools:
        run_command_sync(
            ' '.join(
                [
                    f'dotnet tool install -g {tool}',
                    f'--version {configuration.tool_version}',
                    f'--add-source {configuration.tool_feed}'
                ]
            ),
            log_path=log_path
        )
