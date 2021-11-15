'''Install sdk and tools
'''

import os
import sys
import logging
from urllib import request

import config
from utils import run_command_sync


def install_sdk(configuration: config.TestConfig, logger: logging.Logger):
    '''Install .net(core) sdk
    '''
    logger.info(f'****** install .net sdk ******')
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
        logger.error(f'fail to download install script: {e}.')
        sys.exit(-1)

    command = ' '.join(
        [
            f'{shell_name} {configuration.test_bed}/{os.path.basename(script_url)}',
            f'-InstallDir {sdk_dir} -v {configuration.sdk_version}'
        ]
    )

    rt_code = run_command_sync(command, logger)

    if rt_code == 0:
        logger.info('successfully install sdk!')
        logger.info(f'****** install .net sdk finished ******')
    else:
        logger.error('fail to install sdk!')
        logger.info(f'****** install .net sdk finished ******')
        sys.exit(-1)


def install_tools(configuration: config.TestConfig, logger: logging.Logger):
    '''Install diagnostics
    '''
    logger.info(f'****** install diagnostics tools ******')
    tools = [
        'dotnet-counters',
        'dotnet-dump',
        'dotnet-gcdump',
        'dotnet-sos',
        'dotnet-trace'
    ]
    for tool in tools:
        command = ' '.join(
            [
                f'dotnet tool install {tool}',
                f'--tool-path {configuration.tool_root}',
                f'--version {configuration.tool_version}',
                f'--add-source {configuration.tool_feed}'
            ]
        )
        rt_code = run_command_sync(command, logger)
        if rt_code != 0:
            logger.error(f'fail to install tool: {tool}!')
            logger.info(f'****** install diagnostics tools finished ******')
            sys.exit(-1)
    logger.info(f'****** install diagnostics tools finished ******')
