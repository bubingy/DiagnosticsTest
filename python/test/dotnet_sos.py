# coding=utf-8

import os
import glob
import time

from config import configuration
from utils import run_command_async, run_command_sync, PIPE
from project import projects

log_path = os.path.join(configuration.test_result, 'dotnet_sos.log')


def test_sos():
    '''Run sample apps and perform tests.
    
    '''
    if 'musl' in configuration.rid:
        print('lldb isn\'t available for alpine.')
        return
    webapp_dir = os.path.join(
        configuration.test_bed,
        'webapp'
    )
    sync_commands_list = [
        'dotnet-sos --help',
        'dotnet-sos install',
        'dotnet-sos uninstall',
        'dotnet-sos install',
    ]
    for command in sync_commands_list:
        run_command_sync(command, log_path, cwd=configuration.test_bed)

    # load dump for debugging
    analyze_output_path = os.path.join(configuration.test_result, 'debug-dump.log')
    if 'win' in configuration.rid:
        dump_path = glob.glob(f'{configuration.test_bed}/dump*.dmp')[0]
        plugin_path = os.path.join(
            os.environ['HOME'],
            '.dotnet', 'sos', 'sos.dll'
        )
        analyze_commands = [
            b'sxe ld coreclr\n',
            f'.load {plugin_path}\n'.encode('utf-8'),
            b'!clrstack\n',
            b'!clrthreads\n',
            b'!eestack\n',
            b'!eeheap\n',
            b'!dumpstack\n',
            b'!dumpheap\n',
            b'!dso\n',
            b'!eeversion\n',
            b'.detach\n',
            b'q\n'
        ]
        with open(analyze_output_path, 'w+') as f:
            p = run_command_async(
                f'{configuration.debugger} -z {dump_path}', 
                cwd=configuration.test_result,
                stdin=PIPE,
                stdout=f,
                stderr=f
            )
            for command in analyze_commands:
                p.stdin.write(command)
            p.communicate()

    if 'linux' in configuration.rid:
        dump_path = glob.glob(f'{configuration.test_bed}/core_*')[0]
        analyze_commands = [
            b'clrstack\n',
            b'clrthreads\n',
            b'eestack\n',
            b'eeheap\n',
            b'dumpstack\n',
            b'dumpheap\n',
            b'dso\n',
            b'eeversion\n',
            b'exit\n',
            b'y\n'
        ]
        with open(analyze_output_path, 'w+') as f:
            p = run_command_async(
                f'{configuration.debugger} -c {dump_path}', 
                cwd=configuration.test_result,
                stdin=PIPE,
                stdout=f,
                stderr=f
            )
            for command in analyze_commands:
                p.stdin.write(command)
            p.communicate()

    # attach process for debugging
    webapp = projects.run_webapp(webapp_dir)
    analyze_output_path = os.path.join(configuration.test_result, 'debug-process.log')
    if 'win' in configuration.rid:
        plugin_path = os.path.join(
            os.environ['HOME'],
            '.dotnet', 'sos', 'sos.dll'
        )
        analyze_commands = [
            b'sxe ld coreclr\n',
            f'.load {plugin_path}\n'.encode('utf-8'),
            b'!clrstack\n',
            b'!clrthreads\n',
            b'!eestack\n',
            b'!eeheap\n',
            b'!dumpstack\n',
            b'!dumpheap\n',
            b'!dso\n',
            b'!eeversion\n',
            b'.detach\n',
            b'q\n'
        ]
    else:
        analyze_commands = [
            b'clrstack\n',
            b'clrthreads\n',
            b'eestack\n',
            b'eeheap\n',
            b'dumpstack\n',
            b'dumpheap\n',
            b'dso\n',
            b'eeversion\n',
            b'exit\n',
            b'y\n'
        ]
    with open(analyze_output_path, 'w+') as f:
        p = run_command_async(
            f'{configuration.debugger} -p {webapp.pid}', 
            cwd=configuration.test_result,
            stdin=PIPE,
            stdout=f,
            stderr=f
        )
        for command in analyze_commands:
            p.stdin.write(command)
        p.communicate()
    webapp.terminate()
