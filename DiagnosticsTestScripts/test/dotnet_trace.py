# coding=utf-8

import os

import config
from utils import run_command_async, run_command_sync, PIPE, test_logger
from project import projects


@test_logger(os.path.join(config.configuration.test_result, f'{__name__}.log'))
def test_dotnet_trace(log_path: os.PathLike=None):
    '''Run sample apps and perform tests.

    '''
    if config.configuration.run_webapp is False:
        with open(log_path, 'a+') as f:
            f.write(f'can\'t run webapp for dotnet-trace.\n')
        return
    webapp_dir = os.path.join(
        config.configuration.test_bed,
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
        f'dotnet-trace collect -p {webapp.pid} -o webapp.nettrace --duration 00:00:10',
        stdin=PIPE,
        stdout=PIPE,
        stderr=PIPE,
        cwd=config.configuration.test_result,
    )
    proc.communicate()
    webapp.terminate()
    webapp.communicate()

    run_command_sync(
        'dotnet-trace convert --format speedscope webapp.nettrace',
        log_path,
        cwd=config.configuration.test_result
    )

    if config.configuration.sdk_version[0] == '3':
        print('dotnet-trace new feature isn\'t supported by .net core 3.x')
        return
    if config.configuration.run_consoleapp is False:
        with open(log_path, 'a+') as f:
            f.write(f'can\'t run consoleapp for dotnet-trace.\n')
        return
    consoleapp_dir = os.path.join(
        config.configuration.test_bed,
        'consoleapp'
    )
    extend_name = ''
    if 'win' in config.configuration.rid:
        extend_name = '.exe'
    proc = run_command_async(
        (
            'dotnet-trace collect -o consoleapp.nettrace '
            '--providers Microsoft-Windows-DotNETRuntime '
            f'-- {consoleapp_dir}/out/consoleapp{extend_name}'
        ),
        cwd=config.configuration.test_result
    )
    proc.communicate()
