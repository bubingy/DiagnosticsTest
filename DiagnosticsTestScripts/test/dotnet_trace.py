# coding=utf-8

import os
import time

from config import configuration
from utils import run_command_async, run_command_sync, PIPE
from project import projects

log_path = os.path.join(configuration.test_result, 'dotnet_trace.log')

def test_trace():
    '''Run sample apps and perform tests.

    '''
    if configuration.webappapp_runnable is False:
        with open(log_path, 'a+') as f:
            f.write(f'can\'t run webapp for dotnet-trace.\n')
        return
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

    proc = run_command_async(
        f'dotnet-trace collect -p {webapp.pid} -o webapp.nettrace',
        cwd=configuration.test_bed,
        stdin=PIPE,
        stdout=PIPE,
        stderr=PIPE
    )
    time.sleep(10)
    proc.terminate()
    webapp.terminate()
    run_command_sync(
        'dotnet-trace convert --format speedscope webapp.nettrace',
        log_path,
        cwd=configuration.test_bed
    )

    if configuration.sdk_version[0] == '3':
        print('dotnet-trace new feature isn\'t supported by .net core 3.x')
        return
    if configuration.consoleapp_runnable is False:
        with open(log_path, 'a+') as f:
            f.write(f'can\'t run consoleapp for dotnet-trace.\n')
        return
    consoleapp_dir = os.path.join(
        configuration.test_bed,
        'consoleapp'
    )
    extend_name = ''
    if 'win' in configuration.rid:
        extend_name = '.exe'
    proc = run_command_async(
        'dotnet-trace collect -o consoleapp.nettrace ' + \
            '--providers Microsoft-Windows-DotNETRuntime ' + \
            f'-- {consoleapp_dir}/out/consoleapp{extend_name}',
        cwd=configuration.test_result
    )
    proc.communicate()
