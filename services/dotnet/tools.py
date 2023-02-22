import os
from urllib import request

from utils.terminal import run_command_sync
from utils.logger import ScriptLogger


def install_tool(tool: str, tool_root: os.PathLike, tool_version: str, tool_feed: str, logger: ScriptLogger, dotnet_path: str='dotnet'):
    logger.info(f'install dotnet tool: {tool}')
    command = ' '.join(
        [
            f'{dotnet_path} tool install {tool}',
            f'--tool-path {tool_root}',
            f'--version {tool_version}',
            f'--add-source {tool_feed}'
        ]
    )
    outs, errs = run_command_sync(command)
    logger.info(f'run command:\n{command}\n{outs}')

    if errs != '':
        logger.error(f'fail to install {tool}!\n{errs}')
        raise Exception(f'fail to install tool: {tool}!')
    
    logger.info(f'install diagnostics tools finished')


def install_diagnostics_tools(tool_root: os.PathLike, tool_version: str, tool_feed: str, logger: ScriptLogger, dotnet_path: str='dotnet'):
    '''Install diagnostics
    '''
    logger.info(f'install diagnostics tools')
    tools = [
        'dotnet-counters',
        'dotnet-dump',
        'dotnet-gcdump',
        'dotnet-sos',
        'dotnet-stack',
        'dotnet-trace'
    ]
    for tool in tools:
        install_tool(tool, tool_root, tool_version, tool_feed, logger, dotnet_path)
    logger.info(f'install diagnostics tools finished')


def download_perfcollect(test_bed: os.PathLike, logger: ScriptLogger):
    '''Download perfcollect script.
    '''
    logger.info(f'download perfcollect script')
    req = request.urlopen(
        'https://raw.githubusercontent.com/microsoft/perfview/main/src/perfcollect/perfcollect'
    )
    with open(f'{test_bed}/perfcollect', 'w+') as f:
        f.write(req.read().decode())
    command = f'chmod +x {test_bed}/perfcollect'
    outs, errs = run_command_sync(command)
    logger.info(f'run command:\n{command}\n{outs}')
    if errs != '':
        logger.error(f'fail to make perfcollect runable!\n{errs}')
        logger.info(f'download perfcollect script finished')
        raise Exception(f'fail to make perfcollect runable!')
    logger.info(f'download perfcollect script finished')