# coding=utf-8

import os
import time

from config import configuration
from utils import run_command_async, run_command_sync
from project import projects

log_path = os.path.join(configuration.test_result, 'dotnet_counters.log')

def test_counters():
    '''Run sample apps and perform tests.
    
    '''
    webapp_dir = os.path.join(
        configuration.test_bed,
        'webapp'
    )
    webapp = projects.run_webapp(webapp_dir)
    sync_commands_list = [
        'dotnet-counters --help',
        'dotnet-counters list',
        'dotnet-counters ps'
    ]
    for command in sync_commands_list:
        run_command_sync(command, log_path)

    async_commands_list = [
        f'dotnet-counters collect -p {webapp.pid}',
        f'dotnet-counters monitor -p {webapp.pid}'
    ]
    for command in async_commands_list:
        p = run_command_async(command, cwd=configuration.test_result)
        time.sleep(10)
        p.terminate()
    
    webapp.terminate()

    if configuration.sdk_version[0] == '3':
        print('dotnet-counters new feature isn\'t supported by .net core 3.x')
        return
    consoleapp_dir = os.path.join(
        configuration.test_bed,
        'consoleapp'
    )
    extend_name = ''
    if 'win' in configuration.rid:
        extend_name = '.exe'
    p = run_command_async(
        f'dotnet-counters monitor -- {consoleapp_dir}/out/consoleapp{extend_name}'
    )
    p.communicate()
