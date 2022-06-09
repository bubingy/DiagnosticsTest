# coding=utf-8

import os
import glob
import time
import logging

from DiagnosticsToolsTest import config
from utils.terminal import run_command_sync, run_command_async
from project import project_webapp


def test_dotnet_counters(configuration: config.TestConfig, logger: logging.Logger):
    '''Run sample apps and perform tests.

    '''
    tool_name = 'dotnet-counters'
    tool_path_pattern = f'{configuration.tool_root}/.store/{tool_name}/{configuration.tool_version}/{tool_name}/{configuration.tool_version}/tools/*/any/{tool_name}.dll'
    tool_path = glob.glob(tool_path_pattern)[0]
    tool_bin = f'{configuration.dotnet} {tool_path}'
    
    logger.info(f'test {tool_name}')
    if configuration.run_webapp is False:
        logger.info(f'can\'t run webapp for {tool_name}.')
        logger.info(f'test {tool_name} finished')
        return
    webapp_dir = os.path.join(
        configuration.test_bed,
        'webapp'
    )
    webapp = project_webapp.run_webapp(configuration, webapp_dir)

    sync_commands_list = [
        f'{tool_bin} --help',
        f'{tool_bin}  list',
        f'{tool_bin}  ps'
    ]

    for command in sync_commands_list:
        outs, errs = run_command_sync(command)
        logger.info(f'run command:\n{command}\n{outs}')

        if errs != '': logger.error(errs)

    async_commands_list = [
        f'{tool_bin} collect -p {webapp.pid}',
        f'{tool_bin} monitor -p {webapp.pid}'
    ]
    for command in async_commands_list:
        logger.info(f'run command:\n{command}')
        p = run_command_async(
            command,
            cwd=configuration.test_result
        )
        time.sleep(10)
        p.terminate()

    webapp.terminate()
    webapp.communicate()

    if configuration.sdk_version[0] == '3':
        logger.info(f'{tool_name} new feature isn\'t supported by .net core 3.x.')
        logger.info(f'test {tool_name} finished')
        return
    
    if configuration.run_consoleapp is False:
        logger.info(f'can\'t run consoleapp for {tool_name}.')
        logger.info(f'test {tool_name} finished')
        return

    consoleapp_dir = os.path.join(
        configuration.test_bed,
        'consoleapp'
    )
    extend_name = ''
    if 'win' in configuration.rid:
        extend_name = '.exe'

    command = f'{tool_bin} monitor -- {consoleapp_dir}/out/consoleapp{extend_name}'
    outs, errs = run_command_sync(command)
    logger.info(f'run command:\n{command}')
    logger.info(f'test {tool_name} finished')