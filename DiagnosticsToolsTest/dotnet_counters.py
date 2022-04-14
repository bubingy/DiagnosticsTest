# coding=utf-8

import os
import time
import logging

from DiagnosticsToolsTest import config
from utils.terminal import run_command_sync, run_command_async
from project import project_webapp


def test_dotnet_counters(configuration: config.TestConfig, logger: logging.Logger):
    '''Run sample apps and perform tests.

    '''
    logger.info('test dotnet-counters')
    if configuration.run_webapp is False:
        logger.info('can\'t run webapp for dotnet-counters.')
        logger.info('test dotnet-counters finished')
        return
    webapp_dir = os.path.join(
        configuration.test_bed,
        'webapp'
    )
    webapp = project_webapp.run_webapp(configuration, webapp_dir)
    sync_commands_list = [
        'dotnet-counters --help',
        'dotnet-counters list',
        'dotnet-counters ps'
    ]
    for command in sync_commands_list:
        outs, errs = run_command_sync(command)
        logger.info(f'run command:\n{command}\n{outs}')

        if errs != '': logger.error(errs)

    async_commands_list = [
        f'dotnet-counters collect -p {webapp.pid}',
        f'dotnet-counters monitor -p {webapp.pid}'
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
        logger.info('dotnet-counters new feature isn\'t supported by .net core 3.x.')
        logger.info('test dotnet-counters finished')
        return
    
    if configuration.run_consoleapp is False:
        logger.info('can\'t run consoleapp for dotnet-counters.')
        logger.info('test dotnet-counters finished')
        return

    consoleapp_dir = os.path.join(
        configuration.test_bed,
        'consoleapp'
    )
    extend_name = ''
    if 'win' in configuration.rid:
        extend_name = '.exe'

    command = f'dotnet-counters monitor -- {consoleapp_dir}/out/consoleapp{extend_name}'
    outs, errs = run_command_sync(command)
    logger.info(f'run command:\n{command}')
    logger.info('test dotnet-counters finished')