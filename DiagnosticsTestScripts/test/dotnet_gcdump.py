# coding=utf-8

import os
import glob
import time

import config
from utils import run_command_sync, test_logger
from project import projects


@test_logger(os.path.join(config.configuration.test_result, f'{__name__}.log'))
def test_dotnet_gcdump(log_path: os.PathLike=None):
    '''Run sample apps and perform tests.

    '''
    if config.configuration.run_gcplayground is False:
        message = f'can\'t run gcdumpplayground for dotnet-gcdump.\n'
        print(message)
        with open(log_path, 'a+') as f:
            f.write(message)
        return
    project_dir = os.path.join(
        config.configuration.test_bed,
        'GCDumpPlayground2'
    )
    gcdumpplayground = projects.run_GCDumpPlayground(project_dir)
    sync_commands_list = [
        'dotnet-gcdump --help',
        'dotnet-gcdump ps',
        f'dotnet-gcdump collect -p {gcdumpplayground.pid} -v'
    ]
    for command in sync_commands_list:
        run_command_sync(command, log_path, cwd=config.configuration.test_result)

    gcdumpplayground.terminate()
    while gcdumpplayground.poll() is None:
        time.sleep(1)

    gcdump = glob.glob(f'{config.configuration.test_result}/*.gcdump')
    if len(gcdump) == 0 or gcdump is None:
        message = 'fail to generate gcdump!\n'
        print(message)
        with open(log_path, 'a+') as log:
            log.write(message)
