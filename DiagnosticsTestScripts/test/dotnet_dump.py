# coding=utf-8

import os
import glob

import config
from utils import run_command_async, run_command_sync, PIPE, test_logger
from project import projects


@test_logger(os.path.join(config.configuration.test_result, f'{__name__}.log'))
def test_dotnet_dump(log_path: os.PathLike=None):
    '''Run sample apps and perform tests.

    '''
    if 'osx' in config.configuration.rid and \
        int(config.configuration.sdk_version[0]) < 7:
        message = 'dotnet-dump on osx requires .net 7.0 or newer version.\n'
        print(message)
        with open(log_path, 'a+') as f:
            f.write(message)
        return
    if config.configuration.run_webapp is False:
        message = f'can\'t run webapp for dotnet-dump.\n'
        print(message)
        with open(log_path, 'a+') as f:
            f.write(message)
        return
    webapp_dir = os.path.join(
        config.configuration.test_bed,
        'webapp'
    )
    webapp = projects.run_webapp(webapp_dir)
    sync_commands_list = [
        'dotnet-dump --help',
        'dotnet-dump ps',
        f'dotnet-dump collect -p {webapp.pid}'
    ]
    for command in sync_commands_list:
        run_command_sync(command, log_path, cwd=config.configuration.test_bed)
    webapp.terminate()
    webapp.communicate()

    if 'win' in config.configuration.rid:
        dump_paths = glob.glob(f'{config.configuration.test_bed}/dump*.dmp')
    else:
        dump_paths = glob.glob(f'{config.configuration.test_bed}/core_*')

    if len(dump_paths) == 0:
        message = f'no dump files available.\n'
        print(message)
        with open(log_path, 'a+') as f:
            f.write(message)
        return

    analyze_commands = [
        b'clrstack\n',
        b'clrthreads\n',
        b'clrmodules\n',
        b'eeheap\n',
        b'dumpheap\n',
        b'dso\n',
        b'eeversion\n',
        b'exit\n'
    ]
    analyze_output_path = os.path.join(config.configuration.test_result, 'dotnet_analyze.log')
    with open(analyze_output_path, 'w+') as f:
        proc = run_command_async(
            f'dotnet-dump analyze {dump_paths[0]}', 
            cwd=config.configuration.test_result,
            stdin=PIPE,
            stdout=f,
            stderr=f
        )
        for command in analyze_commands:
            try:
                proc.stdin.write(command)
            except Exception as exception:
                f.write(f'{exception}\n'.encode('utf-8'))
                continue
        proc.communicate()
