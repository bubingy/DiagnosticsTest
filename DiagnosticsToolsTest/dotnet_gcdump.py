# coding=utf-8

import os
import glob
import time
import logging

from DiagnosticsToolsTest import config
from utils.terminal import run_command_sync
from project import project_gcdumpapp


def test_dotnet_gcdump(configuration: config.TestConfig, logger: logging.Logger):
    '''Run sample apps and perform tests.

    '''
    tool_name = 'dotnet-gcdump'
    tool_path_pattern = f'{configuration.tool_root}/.store/{tool_name}/{configuration.tool_version}/{tool_name}/{configuration.tool_version}/tools/*/any/{tool_name}.dll'
    tool_path = glob.glob(tool_path_pattern)[0]
    tool_bin = f'{configuration.dotnet} {tool_path}'
    
    logger.info(f'test {tool_name}')
    if configuration.run_gcplayground is False:
        logger.info(f'can\'t run gcdumpplayground for {tool_name}.')
        logger.info(f'test {tool_name} finished')
        return
    project_dir = os.path.join(
        configuration.test_bed,
        'GCDumpPlayground2'
    )
    gcdumpplayground = project_gcdumpapp.run_GCDumpPlayground(
        configuration,
        project_dir
    )
    
    sync_commands_list = [
        f'{tool_bin} --help',
        f'{tool_bin} ps',
        f'{tool_bin} collect -p {gcdumpplayground.pid} -v'
    ]
    for command in sync_commands_list:
        outs, errs = run_command_sync(command, cwd=configuration.test_result)
        logger.info(f'run command:\n{command}\n{outs}')
        if errs != '': logger.error(errs)

    gcdumpplayground.terminate()
    while gcdumpplayground.poll() is None:
        time.sleep(1)

    gcdump = glob.glob(f'{configuration.test_result}/*.gcdump')
    if len(gcdump) == 0 or gcdump is None:
        logger.error('fail to generate gcdump!')

    logger.info(f'test {tool_name} finished')
