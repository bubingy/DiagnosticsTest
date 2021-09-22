# coding=utf-8

import os
import time

import config
from utils import run_command_async, run_command_sync, test_logger
from project import projects


@test_logger(os.path.join(config.configuration.test_result, f'{__name__}.log'))
def test_dotnet_counters(log_path: os.PathLike=None):
    '''Run sample apps and perform tests.

    '''
    if config.configuration.run_webapp is False:
        with open(log_path, 'a+') as f:
            f.write(f'can\'t run webapp for dotnet-counters.\n')
        return
    webapp_dir = os.path.join(
        config.configuration.test_bed,
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
            p = run_command_async(command, cwd=config.configuration.test_result)
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

    if config.configuration.sdk_version[0] == '3':
        print('dotnet-counters new feature isn\'t supported by .net core 3.x')
        return
    
    if config.configuration.run_consoleapp is False:
        with open(log_path, 'a+') as f:
            f.write(f'can\'t run consoleapp for dotnet-counters.\n')
        return
    consoleapp_dir = os.path.join(
        config.configuration.test_bed,
        'consoleapp'
    )
    extend_name = ''
    if 'win' in config.configuration.rid:
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
