# coding=utf-8

import os
import time

from config import configuration
from utils import run_command_async, run_command_sync
from project import projects

log_path = os.path.join(configuration.test_result, 'dotnet_trace.log')

def test_trace():
    '''Run sample apps and perform tests.
    
    '''
    webapp_dir = os.path.join(
        configuration.test_bed,
        'webapp'
    )
    webapp = projects.run_webapp(webapp_dir)
    sync_commands_list = [
        'dotnet-trace --help',
        'dotnet-trace list-profiles',
        'dotnet-trace ps'
    ]
    for command in sync_commands_list:
        run_command_sync(command, log_path)

    p = run_command_async(
        f'dotnet-trace collect -p {webapp.pid} -o webapp.nettrace', 
        cwd=configuration.test_bed
    )
    time.sleep(10)
    webapp.terminate()
    webapp.communicate()
    p.communicate()
    run_command_sync(
        'dotnet-trace convert --format speedscope webapp.nettrace', 
        log_path,
        cwd=configuration.test_bed
    )

    if configuration.sdk_version[0] == '3':
        print('dotnet-trace new feature isn\'t supported by .net core 3.x')
        return
    consoleapp_dir = os.path.join(
        configuration.test_bed,
        'consoleapp'
    )
    extend_name = ''
    if 'win' in configuration.rid:
        extend_name = '.exe'
    p = run_command_async(
        'dotnet-trace collect -o consoleapp.nettrace ' + \
            '--providers Microsoft-Windows-DotNETRuntime ' + \
            f'-- {consoleapp_dir}/out/consoleapp{extend_name}',
        cwd=configuration.test_result
    )
    p.communicate()
