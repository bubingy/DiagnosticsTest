# coding=utf-8

import os
import glob
import time

from config import configuration
from utils import run_command_async, run_command_sync, PIPE
from project import projects

log_path = os.path.join(configuration.test_result, 'dotnet_dump.log')


def test_dump():
    '''Run sample apps and perform tests.

    '''
    if 'osx' in configuration.rid:
        print('dotnet-dump doesn\'t support on osx.')
        return
    webapp_dir = os.path.join(
        configuration.test_bed,
        'webapp'
    )
    webapp = projects.run_webapp(webapp_dir)
    sync_commands_list = [
        'dotnet-dump --help',
        'dotnet-dump ps',
        f'dotnet-dump collect -p {webapp.pid}'
    ]
    for command in sync_commands_list:
        run_command_sync(command, log_path, cwd=configuration.test_bed)
    webapp.terminate()
    while webapp.poll() is None:
        time.sleep(1)

    if 'win' in configuration.rid:
        dump_path = glob.glob(f'{configuration.test_bed}/dump*.dmp')[0]
    else:
        dump_path = glob.glob(f'{configuration.test_bed}/core_*')[0]

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
    analyze_output_path = os.path.join(configuration.test_result, 'dotnet_analyze.log')
    with open(analyze_output_path, 'w+') as f:
        proc = run_command_async(
            f'dotnet-dump analyze {dump_path}', 
            cwd=configuration.test_result,
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
