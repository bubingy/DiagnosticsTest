'''Install sdk and tools
'''

import os
from urllib import request

from config import TestConfig
from utils import run_command_sync, Result


def prepare_test_bed(conf: TestConfig):
    '''Create folders for TestBed.
    '''
    try:
        if not os.path.exists(conf.test_bed):
            os.makedirs(conf.test_bed)
        if not os.path.exists(conf.trace_directory):
            os.makedirs(conf.trace_directory)
    except Exception as e:
        print(e)
        exit(-1)


def download_perfcollect(conf: TestConfig):
    '''Download perfcollect script.
    '''
    req = request.urlopen(
        'https://raw.githubusercontent.com/microsoft/perfview/main/src/perfcollect/perfcollect'
    )
    with open(f'{conf.test_bed}/perfcollect', 'w+') as f:
        f.write(req.read().decode())
    run_command_sync(f'chmod +x {conf.test_bed}/perfcollect')


def install_sdk(conf: TestConfig, arch: str='x64'):
    '''Install .net(core) sdk
    '''
    if 'win' in conf.rid:
        req = request.urlopen('https://dot.net/v1/dotnet-install.ps1')
        with open(f'{conf.test_bed}/dotnet-install.ps1', 'w+') as f:
            f.write(req.read().decode())
        rt_code = run_command_sync(
            ' '.join(
                [
                    f'powershell.exe {conf.test_bed}/dotnet-install.ps1',
                    f'-InstallDir {conf.dotnet_root} -v {conf.sdk_version} -Architecture {arch}'
                ]
            )
        )
    else:
        req = request.urlopen(
            'https://dotnet.microsoft.com/download/dotnet-core/scripts/v1/dotnet-install.sh'
        )
        with open(f'{conf.test_bed}/dotnet-install.sh', 'w+') as f:
            f.write(req.read().decode())
        run_command_sync(f'chmod +x {conf.test_bed}/dotnet-install.sh')
        if conf.rid == 'linux-musl-arm64':
            rt_code = run_command_sync(
                (
                    f'/bin/bash {conf.test_bed}/dotnet-install.sh '
                    f'-InstallDir {conf.dotnet_root} '
                    f'-v {conf.runtime_version} --runtime dotnet'
                )
            )
        else:
            rt_code = run_command_sync(
                ' '.join(
                    [
                        f'/bin/bash {conf.test_bed}/dotnet-install.sh',
                        f'-InstallDir {conf.dotnet_root} -v {conf.sdk_version}'
                    ]
                )
            )
    if rt_code == 0:
        return Result(0, 'successfully install sdk', None)
    else:
        return Result(rt_code, 'fail to install sdk', None)
