# coding=utf-8

import os
import glob
import logging

from DiagnosticsToolsTest import config
from utils.terminal import run_command_sync, run_command_async, PIPE
from project import project_webapp


def test_dotnet_dump(configuration: config.TestConfig, logger: logging.Logger):
    '''Run sample apps and perform tests.

    '''
    logger.info('test dotnet-dump')
    if 'osx' in configuration.rid and \
        int(configuration.sdk_version[0]) < 7:
        logger.info('dotnet-dump on osx requires .net 7.0 or newer version.')
        logger.info('test dotnet-dump finished')
        return
    if configuration.run_webapp is False:
        logger.info('can\'t run webapp for dotnet-dump.')
        logger.info('test dotnet-dump finished')
        return
    webapp_dir = os.path.join(
        configuration.test_bed,
        'webapp'
    )
    webapp = project_webapp.run_webapp(configuration, webapp_dir)
    sync_commands_list = [
        'dotnet-dump --help',
        'dotnet-dump ps',
        f'dotnet-dump collect -p {webapp.pid}'
    ]
    for command in sync_commands_list:
        outs, errs = run_command_sync(command, cwd=configuration.test_bed)
        logger.info(f'run command:\n{command}\n{outs}')
        if errs != '': logger.error(errs)

    webapp.terminate()
    webapp.communicate()

    if 'win' in configuration.rid:
        dump_paths = glob.glob(f'{configuration.test_bed}/dump*.dmp')
    else:
        dump_paths = glob.glob(f'{configuration.test_bed}/core_*')

    if len(dump_paths) == 0:
        logger.error('no dump files available.')
        logger.info('test dotnet-dump finished')
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
    analyze_output_path = os.path.join(configuration.test_result, 'dotnet_analyze.log')
    with open(analyze_output_path, 'w+') as f:
        command = f'dotnet-dump analyze {dump_paths[0]}'
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

    logger.info('test dotnet-dump finished')
