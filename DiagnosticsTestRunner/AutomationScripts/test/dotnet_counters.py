# coding=utf-8

import os
import time

from AutomationScripts.config import configuration
from AutomationScripts.utils import run_command_async, run_command_sync
from AutomationScripts.project import projects

log_path = os.path.join(configuration.test_result, 'dotnet_counters.log')

def test_counters():
    '''Run sample apps and perform tests.

    '''
    if configuration.webappapp_runnable is False:
        with open(log_path, 'a+') as f:
            f.write(f'can\'t run webapp for dotnet-counters.\n')
        return
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
        try:
            p = run_command_async(command, cwd=configuration.test_result)
            time.sleep(10)
            p.terminate()
            with open(log_path, 'a+') as f:
                f.write(f'successfully run command {command}\n')
        except Exception as exception:
            with open(log_path, 'a+') as f:
                f.write(f'fail to run command: {exception}\n')
            continue

    webapp.terminate()
    webapp.communicate()

    if configuration.sdk_version[0] == '3':
        print('dotnet-counters new feature isn\'t supported by .net core 3.x')
        return
    
    if configuration.consoleapp_runnable is False:
        with open(log_path, 'a+') as f:
            f.write(f'can\'t run consoleapp for dotnet-counters.\n')
        return
    consoleapp_dir = os.path.join(
        configuration.test_bed,
        'consoleapp'
    )
    extend_name = ''
    if 'win' in configuration.rid:
        extend_name = '.exe'
    try:
        p = run_command_async(
            f'dotnet-counters monitor -- {consoleapp_dir}/out/consoleapp{extend_name}'
        )
        p.communicate()
        with open(log_path, 'a+') as f:
            f.write(f'successfully run command {command}\n')
    except Exception as exception:
        with open(log_path, 'a+') as f:
            f.write(f'fail to run command: {exception}\n')
