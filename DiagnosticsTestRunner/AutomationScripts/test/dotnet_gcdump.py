# coding=utf-8

import os
import glob
import time

from config import configuration
from utils import run_command_async, run_command_sync
from project import projects

log_path = os.path.join(configuration.test_result, 'dotnet_gcdump.log')

def test_gcdump():
    '''Run sample apps and perform tests.

    '''
    if configuration.gcplayground_runnable is False:
        with open(log_path, 'a+') as f:
            f.write(f'can\'t run gcdumpplayground for dotnet-gcdump.\n')
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
        run_command_sync(command, log_path, cwd=configuration.test_result)
    gcdumpplayground.terminate()
    while gcdumpplayground.poll() is None:
        time.sleep(1)

    gcdump = glob.glob(f'{configuration.test_result}/*.gcdump')
    if len(gcdump) == 0 or gcdump is None:
        print('fail to generate gcdump.')
        with open(log_path, 'a+') as log:
            log.write('fail to generate gcdump\n')
