# coding=utf-8

import os
import glob
import time
import logging

from DiagnosticsToolsTest import config
from utils.terminal import run_command_sync
from project import project_webapp


def test_dotnet_stack(configuration: config.TestConfig, logger: logging.Logger):
    '''Run sample apps and perform tests.

    '''
    tool_name = 'dotnet-stack'
    tool_path_pattern = f'{configuration.tool_root}/.store/{tool_name}/{configuration.tool_version}/{tool_name}/{configuration.tool_version}/tools/*/any/{tool_name}.dll'
    tool_path = glob.glob(tool_path_pattern)[0]
    tool_bin = f'{configuration.dotnet} {tool_path}'
    
    logger.info(f'test {tool_name}')
    if configuration.run_webapp is False:
        logger.info(f'can\'t run webapp for {tool_name}.')
        logger.info(f'test {tool_name} finished')
        return
    project_dir = os.path.join(
        configuration.test_bed,
        'webapp'
    )
    webapp = project_webapp.run_webapp(
        configuration,
        project_dir
    )
    
    sync_commands_list = [
        f'{tool_bin} --help',
        f'{tool_bin} ps',
        f'{tool_bin} report -p {webapp.pid}'
    ]
    for command in sync_commands_list:
        outs, errs = run_command_sync(command, cwd=configuration.test_result)
        logger.info(f'run command:\n{command}\n{outs}')
        if errs != '': logger.error(errs)

    webapp.terminate()
    while webapp.poll() is None:
        time.sleep(1)

    logger.info(f'test {tool_name} finished')
