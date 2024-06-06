import os
import glob
import time
from subprocess import PIPE

import app
from tools import dotnet_tool
from tools import terminal
from tools.sysinfo import SysInfo
from DiagnosticTools.configuration import DiagToolsTestConfiguration
from DiagnosticTools import target_app


def __get_analyze_commands(rid: str):
    if 'win' in rid:
        home_path = os.environ['USERPROFILE']
        plugin_path = os.path.join(
            home_path, '.dotnet', 'sos', 'sos.dll'
        )
        return [
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
        return [
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


@app.function_monitor(
    pre_run_msg='------ start to test dotnet-sos ------',
    post_run_msg='------ test dotnet-sos completed ------'
)
def test_dotnet_sos(test_conf: DiagToolsTestConfiguration):
    '''Run sample apps and perform tests.

    '''
    tool_dll_path = dotnet_tool.get_tool_dll(
        'dotnet-sos',
        test_conf.diag_tool_version,
        test_conf.diag_tool_root
    )
    if isinstance(tool_dll_path, Exception):
        return tool_dll_path

    sync_args_list = [
        [test_conf.dotnet_bin_path, tool_dll_path, '--help'],
        [test_conf.dotnet_bin_path, tool_dll_path, 'install'],
        [test_conf.dotnet_bin_path, tool_dll_path, 'uninstall'],
        [test_conf.dotnet_bin_path, tool_dll_path, 'install'],
    ]
    for args in sync_args_list:
        _, outs, errs = terminal.run_command_sync(
            args,
            cwd=test_conf.test_bed,
            env=test_conf.env,
        )
    debug_dump(test_conf)
    attach_process(test_conf)
    
    
@app.function_monitor(
    pre_run_msg='------ start to debug dump file ------',
    post_run_msg='------ debug dump file completed ------'
)
def debug_dump(test_conf: DiagToolsTestConfiguration):
    '''Debug a dump
    
    '''
    if isinstance(SysInfo.debugger, Exception):
        return SysInfo.debugger

    if 'win' in SysInfo.rid:
        dump_path_template = os.path.join(test_conf.test_bed, 'dump*.dmp')
    else:
        dump_path_template = os.path.join(test_conf.test_bed, 'core_*')

    dump_path_candidates = glob.glob(dump_path_template)
    if len(dump_path_candidates) < 1:
        return Exception('no dump file is generated')
    
    dump_path = dump_path_candidates[0]
    analyze_output = os.path.join(test_conf.test_result_folder, 'sos_dump_debug.log')

    analyze_commands = __get_analyze_commands(SysInfo.rid)
    if 'win' in SysInfo.rid:
        debug_script = os.path.join(
            test_conf.test_bed,
            'cdb_debug_script'
        )
        with open(debug_script, 'wb+') as fs:
            fs.writelines(analyze_commands)

        args = [SysInfo.debugger, '-z', dump_path, '-cf', debug_script]
        with open(analyze_output, 'wb+') as fp:
            command, proc = terminal.run_command_async(args, stdout=fp, stderr=fp, env=test_conf.env)
            proc.communicate()

    else:
        args = [SysInfo.debugger, '-c', dump_path]
        with open(analyze_output, 'wb+') as fp:
            command, proc = terminal.run_command_async(args, stdin=PIPE, stdout=fp, stderr=fp, env=test_conf.env)
            for command in analyze_commands:
                try:
                    proc.stdin.write(command)
                except Exception as exception:
                    fp.write(f'{exception}\n'.encode('utf-8'))
                    continue
            proc.communicate()


@app.function_monitor(
    pre_run_msg='------ start to attach process ------',
    post_run_msg='------ attach process completed ------'
)
def attach_process(test_conf: DiagToolsTestConfiguration):
    '''Attach then debug a process
    
    '''
    if isinstance(SysInfo.debugger, Exception):
        return SysInfo.debugger
    
    webapp_process = target_app.run_webapp(test_conf)
    if isinstance(webapp_process, Exception):
        return webapp_process
    
    analyze_output = os.path.join(test_conf.test_result_folder, 'sos_process_debug.log')
    analyze_commands = __get_analyze_commands(SysInfo.rid)

    if 'win' in SysInfo.rid:
        debug_script = os.path.join(
            test_conf.test_bed,
            'cdb_debug_script'
        )
        with open(debug_script, 'wb+') as fs:
            fs.writelines(analyze_commands)

        args = [SysInfo.debugger, '-p', str(webapp_process.pid), '-cf', debug_script]
        with open(analyze_output, 'wb+') as fp:
            command, proc = terminal.run_command_async(args, stdout=fp, stderr=fp, env=test_conf.env)
            proc.communicate()
    else:
        args = [SysInfo.debugger, '-p', str(webapp_process.pid)]
        with open(analyze_output, 'wb+') as fp:
            command, proc = terminal.run_command_async(args, stdin=PIPE, stdout=fp, stderr=fp, env=test_conf.env)
            for command in analyze_commands:
                try:
                    proc.stdin.write(command)
                except Exception as exception:
                    fp.write(f'{exception}\n'.encode('utf-8'))
                    continue
            proc.communicate()

    webapp_process.terminate()
    while webapp_process.poll() is None:
        time.sleep(1)