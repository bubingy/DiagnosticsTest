import os
import glob

from instances.config import DiagnosticToolsTest as diag_tools_test_conf
from instances.logger import ScriptLogger
from instances.project import webapp as webapp_config
from services.terminal import run_command_sync, run_command_async, PIPE
from services.project import webapp as webapp_service


def test_dotnet_sos(logger: ScriptLogger):
    '''Run sample apps and perform tests.

    '''
    tool_name = 'dotnet-sos'
    tool_path_pattern = (
        f'{diag_tools_test_conf.tool_root}/.store/{tool_name}'
        f'/{diag_tools_test_conf.tool_version}/{tool_name}'
        f'/{diag_tools_test_conf.tool_version}/tools/*/any/{tool_name}.dll'
    )
    tool_path = glob.glob(tool_path_pattern)[0]
    tool_bin = f'{diag_tools_test_conf.dotnet_bin_path} {tool_path}'

    logger.info(f'test {tool_name}')
    if 'musl' in diag_tools_test_conf.rid:
        logger.warning('lldb isn\'t available for alpine.')
        logger.info(f'test {tool_name} finished')
        return
    
    if webapp_config.runnable is False:
        logger.warning(f'can\'t run webapp for {tool_name}.')
        logger.info(f'test {tool_name} finished')
        return

    sync_commands_list = [
        f'{tool_bin} --help',
        f'{tool_bin} install',
        f'{tool_bin} uninstall',
        f'{tool_bin} install',
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

    # test sos command 
    if 'win' in diag_tools_test_conf.rid:
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
            diag_tools_test_conf.testbed,
            'cdb_debug_script'
        )
        with open(debug_script, 'wb+') as fs:
            fs.writelines(analyze_commands)

        dump_path_candidate = glob.glob(f'{diag_tools_test_conf.testbed}/dump*.dmp')
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
        dump_path_candidate = glob.glob(f'{diag_tools_test_conf.testbed}/core_*')

    # load dump for debugging
    analyze_output_path = os.path.join(diag_tools_test_conf.test_result_root, 'sos_debug_dump.log')

    if 'win' in diag_tools_test_conf.rid:
        if len(dump_path_candidate) < 1:
            logger.warning('no dump available.')
        else:
            dump_path = dump_path_candidate[0]
            try:
                with open(analyze_output_path, 'w+') as fs:
                    command = f'{diag_tools_test_conf.debugger} -z {dump_path} -cf {debug_script}'
                    logger.info(f'run command:\n{command}')
                    run_command_async(
                        command,
                        env=diag_tools_test_conf.env,
                        stdout=fs,
                        stderr=fs
                    ).communicate()
            except Exception as e:
                logger.error(f'fail to debug dumpfile: {e}')
    else:
        if len(dump_path_candidate) < 1:
            logger.warning('no dump available.')
        else:
            dump_path = dump_path_candidate[0]
            try:
                with open(analyze_output_path, 'w+') as f:
                    command = f'{diag_tools_test_conf.debugger} -c {dump_path}'
                    logger.info(f'run command:\n{command}')
                    proc = run_command_async(
                        command,
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
            except Exception as e:
                logger.error(f'fail to debug dumpfile: {e}')

    # attach process for debugging
    webapp_process = webapp_service.run_webapp(diag_tools_test_conf.env, diag_tools_test_conf.testbed)

    analyze_output_path = os.path.join(diag_tools_test_conf.test_result_root, 'sos_debug_process.log')

    if 'win' in diag_tools_test_conf.rid:
        with open(analyze_output_path, 'w+') as fs:
            command = f'{diag_tools_test_conf.debugger} -p {webapp_process.pid} -cf {debug_script}'
            logger.info(f'run command:\n{command}')
            run_command_async(
                command,
                env=diag_tools_test_conf.env,
                stdout=fs,
                stderr=fs
            ).communicate()
    else:
        with open(analyze_output_path, 'w+') as f:
            command =  f'{diag_tools_test_conf.debugger} -p {webapp_process.pid}'
            logger.info(f'run command:\n{command}')
            proc = run_command_async(
                command,
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
    webapp_process.terminate()
    webapp_process.communicate()

    logger.info(f'test {tool_name} finished')
