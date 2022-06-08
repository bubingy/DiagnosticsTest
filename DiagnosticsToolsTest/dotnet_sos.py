# coding=utf-8

import os
import glob
import logging

from DiagnosticsToolsTest import config
from utils.terminal import run_command_sync, run_command_async, PIPE
from project import project_webapp


def test_dotnet_sos(configuration: config.TestConfig, logger: logging.Logger):
    '''Run sample apps and perform tests.

    '''
    logger.info('test dotnet-sos')
    if 'musl' in configuration.rid:
        logger.warning('lldb isn\'t available for alpine.')
        logger.info('test dotnet-sos finished')
        return
    
    if configuration.run_webapp is False:
        logger.warning('can\'t run webapp for dotnet-sos.')
        logger.info('test dotnet-sos finished')
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
        outs, errs = run_command_sync(command, cwd=configuration.test_bed)
        logger.info(f'run command:\n{command}\n{outs}')
        if errs != '': logger.error(errs)

    if 'win' in configuration.rid:
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
            configuration.test_bed,
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
    
    # eestack and dumpstack commands are not reliable
    if configuration.rid == 'linux-arm':
        analyze_commands.remove(b'eestack\n')
        analyze_commands.remove(b'dumpstack\n')
        analyze_commands.insert(0, b'clrstack -f\n')

    # load dump for debugging
    analyze_output_path = os.path.join(configuration.test_result, 'debug_dump.log')
    if 'win' in configuration.rid:
        try:
            dump_path = glob.glob(f'{configuration.test_bed}/dump*.dmp')[0]
            with open(analyze_output_path, 'w+') as fs:
                command = f'{configuration.debugger} -z {dump_path} -cf {debug_script}'
                logger.info(f'run command:\n{command}')
                run_command_async(
                    command,
                    stdout=fs,
                    stderr=fs
                ).communicate()
        except Exception as e:
            logger.error(f'fail to debug dumpfile: {e}')
    if 'linux' in configuration.rid or \
        (
            'osx' in configuration.rid and \
        int(configuration.sdk_version[0]) >= 7
        ):
        try:
            dump_path = glob.glob(f'{configuration.test_bed}/core_*')[0]
            with open(analyze_output_path, 'w+') as f:
                command = f'{configuration.debugger} -c {dump_path}'
                logger.info(f'run command:\n{command}')
                proc = run_command_async(
                    command,
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
        except Exception as e:
            logger.error(f'fail to debug dumpfile: {e}')

    # attach process for debugging
    webapp = project_webapp.run_webapp(configuration, webapp_dir)
    analyze_output_path = os.path.join(configuration.test_result, 'debug_process.log')
    if 'win' in configuration.rid:
        with open(analyze_output_path, 'w+') as fs:
            command = f'{configuration.debugger} -p {webapp.pid} -cf {debug_script}'
            logger.info(f'run command:\n{command}')
            run_command_async(
                command,
                stdout=fs,
                stderr=fs
            ).communicate()
    else:
        with open(analyze_output_path, 'w+') as f:
            command =  f'{configuration.debugger} -p {webapp.pid}'
            logger.info(f'run command:\n{command}')
            proc = run_command_async(
                command,
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
    webapp.terminate()
    webapp.communicate()

    logger.info('test dotnet-sos finished')
