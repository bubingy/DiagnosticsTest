import os
import glob

from instances.config import DiagnosticToolsTest as diag_tools_test_conf
from instances.logger import ScriptLogger
from instances.project import webapp as webapp_config
from services.terminal import run_command_sync, run_command_async, PIPE
from services.project import webapp as webapp_service


def test_dotnet_dump(logger: ScriptLogger):
    '''Run sample apps and perform tests.

    '''
    tool_name = 'dotnet-dump'
    tool_path_pattern = (
        f'{diag_tools_test_conf.tool_root}/.store/{tool_name}'
        f'/{diag_tools_test_conf.tool_version}/{tool_name}'
        f'/{diag_tools_test_conf.tool_version}/tools/*/any/{tool_name}.dll'
    )
    tool_path = glob.glob(tool_path_pattern)[0]
    tool_bin = f'{diag_tools_test_conf.dotnet_bin_path} {tool_path}'

    logger.info(f'test {tool_name}')
    if 'osx' in diag_tools_test_conf.rid and \
        int(diag_tools_test_conf.sdk_version[0]) < 7:
        logger.info(f'{tool_name} on osx requires .net 7.0 or newer version.')
        logger.info(f'test {tool_name} finished')
        return
    if webapp_config.runnable is False:
        logger.info(f'can\'t run webapp for {tool_name}.')
        logger.info(f'test {tool_name} finished')
        return
    
    webapp_process = webapp_service.run_webapp(diag_tools_test_conf.env, diag_tools_test_conf.testbed)

    sync_commands_list = [
        f'{tool_bin} --help',
        f'{tool_bin} ps',
        f'{tool_bin} collect -p {webapp_process.pid}'
    ]
    for command in sync_commands_list:
        outs, errs = run_command_sync(
            command,
            cwd=diag_tools_test_conf.testbed,
            env=diag_tools_test_conf.env,
            stdout=PIPE,
            stderr=PIPE
        )
        logger.info(f'run command:\n{command}\n{outs}')
        if errs != '': logger.error(errs)

    webapp_process.terminate()
    webapp_process.communicate()

    if 'win' in diag_tools_test_conf.rid:
        dump_paths = glob.glob(f'{diag_tools_test_conf.testbed}/dump*.dmp')
    else:
        dump_paths = glob.glob(f'{diag_tools_test_conf.testbed}/core_*')

    if len(dump_paths) == 0:
        logger.error('no dump files available.')
        logger.info(f'test {tool_name} finished')
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
    analyze_output_path = os.path.join(
        diag_tools_test_conf.test_result_root,
        'dotnet_analyze.log'
    )
    with open(analyze_output_path, 'w+') as f:
        command = f'{tool_bin} analyze {dump_paths[0]}'
        logger.info(f'run command:\n{command}')
        proc = run_command_async(
            command,
            cwd=diag_tools_test_conf.test_result_root,
            env=diag_tools_test_conf.env,
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

    logger.info(f'test {tool_name} finished')
