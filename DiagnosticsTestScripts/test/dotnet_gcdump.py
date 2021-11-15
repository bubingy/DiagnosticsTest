# coding=utf-8

import os
import glob
import time
import logging

import config
from utils import run_command_sync
from project import projects


def test_dotnet_gcdump(configuration: config.TestConfig, logger: logging.Logger):
    '''Run sample apps and perform tests.

    '''
    logger.info('****** test dotnet-gcdump ******')
    if configuration.run_gcplayground is False:
        logger.info('can\'t run gcdumpplayground for dotnet-gcdump.')
        logger.info('****** test dotnet-gcdump finished ******')
        return
    project_dir = os.path.join(
        configuration.test_bed,
        'GCDumpPlayground2'
    )
    gcdumpplayground = projects.run_GCDumpPlayground(project_dir)
    sync_commands_list = [
        'dotnet-gcdump --help',
        'dotnet-gcdump ps',
        f'dotnet-gcdump collect -p {gcdumpplayground.pid} -v'
    ]
    for command in sync_commands_list:
        run_command_sync(command, logger, cwd=configuration.test_result)

    gcdumpplayground.terminate()
    while gcdumpplayground.poll() is None:
        time.sleep(1)

    gcdump = glob.glob(f'{configuration.test_result}/*.gcdump')
    if len(gcdump) == 0 or gcdump is None:
        logger.error('fail to generate gcdump!')

    logger.info('****** test dotnet-gcdump finished ******')
