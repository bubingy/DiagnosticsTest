# coding=utf-8

import os
import glob

import config
from utils import run_command_async, run_command_sync, PIPE, test_logger
from project import projects


@test_logger(os.path.join(config.configuration.test_result, f'{__name__}.log'))
def test_dotnet_sos(log_path: os.PathLike=None):
    '''Run sample apps and perform tests.

    '''
    if 'musl' in config.configuration.rid:
        print('lldb isn\'t available for alpine.')
        return
    
    if config.configuration.run_webapp is False:
        with open(log_path, 'a+') as f:
            f.write(f'can\'t run webapp for dotnet-sos.\n')
        return

    webapp_dir = os.path.join(
        config.configuration.test_bed,
        'webapp'
    )
    sync_commands_list = [
        'dotnet-sos --help',
        'dotnet-sos install',
        'dotnet-sos uninstall',
        'dotnet-sos install',
    ]
    for command in sync_commands_list:
        run_command_sync(command, log_path, cwd=config.configuration.test_bed)

    if 'win' in config.configuration.rid:
        home_path = os.environ['USERPROFILE']
        plugin_path = os.path.join(
            home_path,
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
        debug_script = os.path.join(
            config.configuration.test_bed,
            'cdb_debug_script'
        )
        with open(debug_script, 'wb+') as fs:
            fs.writelines(analyze_commands)
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
    
    # load dump for debugging
    analyze_output_path = os.path.join(config.configuration.test_result, 'debug_dump.log')
    if 'win' in config.configuration.rid:
        dump_path = glob.glob(f'{config.configuration.test_bed}/dump*.dmp')[0]
        with open(analyze_output_path, 'w+') as fs:
            run_command_async(
                (
                    f'{config.configuration.debugger} -z {dump_path} '
                    f'-cf {debug_script}'
                ),
                log_path=log_path,
                stdout=fs,
                stderr=fs
            ).communicate()

    if 'linux' in config.configuration.rid:
        dump_path = glob.glob(f'{config.configuration.test_bed}/core_*')[0]
        with open(analyze_output_path, 'w+') as f:
            proc = run_command_async(
                f'{config.configuration.debugger} -c {dump_path}',
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

    # attach process for debugging
    webapp = projects.run_webapp(webapp_dir)
    analyze_output_path = os.path.join(config.configuration.test_result, 'debug_process.log')
    if 'win' in config.configuration.rid:
        with open(analyze_output_path, 'w+') as fs:
            run_command_async(
                (
                    f'{config.configuration.debugger} -p {webapp.pid} '
                    f'-cf {debug_script}'
                ),
                log_path=log_path,
                stdout=fs,
                stderr=fs
            ).communicate()
    else:
        with open(analyze_output_path, 'w+') as f:
            proc = run_command_async(
                f'{config.configuration.debugger} -p {webapp.pid}',
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
    webapp.terminate()
    webapp.communicate()
