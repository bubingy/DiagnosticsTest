# coding=utf-8

import os
import logging

from DiagnosticsToolsTest import config
from utils.terminal import run_command_sync
from project import project_webapp


def test_dotnet_trace(configuration: config.TestConfig, logger: logging.Logger):
    '''Run sample apps and perform tests.

    '''
    logger.info('test dotnet-trace')
    if configuration.run_webapp is False:
        logger.info('can\'t run webapp for dotnet-trace.')
        logger.info('test dotnet-trace finished')
        return
    webapp_dir = os.path.join(
        configuration.test_bed,
        'webapp'
    )
    webapp = project_webapp.run_webapp(configuration, webapp_dir)
    sync_commands_list = [
        'dotnet-trace --help',
        'dotnet-trace list-profiles',
        'dotnet-trace ps',
        f'dotnet-trace collect -p {webapp.pid} -o webapp.nettrace --duration 00:00:10',
        'dotnet-trace convert --format speedscope webapp.nettrace'
    ]
    for command in sync_commands_list:
        outs, errs = run_command_sync(command, cwd=configuration.test_result)
        logger.info(f'run command:\n{command}\n{outs}')
        if errs != '': logger.error(errs)

    webapp.terminate()
    webapp.communicate()

    if configuration.sdk_version[0] == '3':
        logger.info('dotnet-trace new feature isn\'t supported by .net core 3.x.')
        logger.info('test dotnet-trace finished')
        return

    if configuration.run_consoleapp is False:
        logger.info('can\'t run consoleapp for dotnet-trace.')
        logger.info('test dotnet-trace finished')
        return

    consoleapp_dir = os.path.join(
        configuration.test_bed,
        'consoleapp'
    )
    extend_name = ''
    if 'win' in configuration.rid:
        extend_name = '.exe'

    command = (
        'dotnet-trace collect -o consoleapp.nettrace '
        '--providers Microsoft-Windows-DotNETRuntime '
        f'-- {consoleapp_dir}/out/consoleapp{extend_name}'
    )
    
    outs, errs = run_command_sync(
        command,
        cwd=configuration.test_result
    )
    logger.info(f'run command:\n{command}\n{outs}')
    if errs != '': logger.error(errs)

    logger.info('test dotnet-trace finished')