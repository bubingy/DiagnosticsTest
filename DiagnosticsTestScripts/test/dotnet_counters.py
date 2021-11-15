# coding=utf-8

import os
import time
import logging

import config
from utils import run_command_async, run_command_sync
from project import projects


def test_dotnet_counters(configuration: config.TestConfig, logger: logging.Logger):
    '''Run sample apps and perform tests.

    '''
    logger.info('****** test dotnet-counters ******')
    if configuration.run_webapp is False:
        logger.info('can\'t run webapp for dotnet-counters.')
        logger.info('****** test dotnet-counters finished ******')
        return
    webapp_dir = os.path.join(
        configuration.test_bed,
        'webapp'
    )
    webapp = projects.run_webapp(configuration, logger, webapp_dir)
    sync_commands_list = [
        'dotnet-counters --help',
        'dotnet-counters list',
        'dotnet-counters ps'
    ]
    for command in sync_commands_list:
        run_command_sync(command, logger)
        
    async_commands_list = [
        f'dotnet-counters collect -p {webapp.pid}',
        f'dotnet-counters monitor -p {webapp.pid}'
    ]
    for command in async_commands_list:
        p = run_command_async(
            command,
            logger,
            cwd=configuration.test_result
        )
        time.sleep(10)
        p.terminate()

    webapp.terminate()
    webapp.communicate()

    if configuration.sdk_version[0] == '3':
        logger.info('dotnet-counters new feature isn\'t supported by .net core 3.x.')
        logger.info('****** test dotnet-counters finished ******')
        return
    
    if configuration.run_consoleapp is False:
        logger.info('can\'t run consoleapp for dotnet-counters.')
        logger.info('****** test dotnet-counters finished ******')
        return

    consoleapp_dir = os.path.join(
        configuration.test_bed,
        'consoleapp'
    )
    extend_name = ''
    if 'win' in configuration.rid:
        extend_name = '.exe'

    p = run_command_async(
        f'dotnet-counters monitor -- {consoleapp_dir}/out/consoleapp{extend_name}',
        logger
    )
    p.communicate()

    logger.info('****** test dotnet-counters finished ******')