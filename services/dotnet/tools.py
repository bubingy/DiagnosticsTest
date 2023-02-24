import os
from urllib import request

from instances.logger import ScriptLogger
from services.terminal import run_command_sync, PIPE


def install_tool(dotnet_bin_path: str, 
                tool: str, 
                tool_root: os.PathLike, 
                tool_version: str, 
                tool_feed: str,
                env: dict,
                logger: ScriptLogger):
    logger.info(f'install dotnet tool: {tool}')
    command = ' '.join(
        [
            f'{dotnet_bin_path} tool install {tool}',
            f'--tool-path {tool_root}',
            f'--version {tool_version}',
            f'--add-source {tool_feed}'
        ]
    )
    outs, errs = run_command_sync(command, env=env, stdout=PIPE, stderr=PIPE)
    logger.info(f'run command:\n{command}\n{outs}')

    if errs != '':
        logger.error(f'fail to install {tool}!\n{errs}')
        raise Exception(f'fail to install tool: {tool}!')
    
    logger.info(f'install {tool} finished')


def install_diagnostic_tools(dotnet_bin_path: str, 
                            tool_root: os.PathLike, 
                            tool_version: str, 
                            tool_feed: str,
                            env: dict,
                            logger: ScriptLogger):
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
        install_tool(dotnet_bin_path, tool, tool_root, tool_version, tool_feed, env, logger)
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
    outs, errs = run_command_sync(command, stdout=PIPE, stderr=PIPE)
    logger.info(f'run command:\n{command}\n{outs}')
    if errs != '':
        logger.error(f'fail to make perfcollect runable!\n{errs}')
        logger.info(f'download perfcollect script finished')
        raise Exception(f'fail to make perfcollect runable!')
    logger.info(f'download perfcollect script finished')