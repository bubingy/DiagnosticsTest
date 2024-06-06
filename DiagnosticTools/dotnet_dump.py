import os
import time
import glob
from subprocess import PIPE

import app
from tools import dotnet_tool
from tools import terminal
from tools.sysinfo import SysInfo
from DiagnosticTools.configuration import DiagToolsTestConfiguration
from DiagnosticTools import target_app


@app.function_monitor(
    pre_run_msg='------ start to test dotnet-dump ------',
    post_run_msg='------ test dotnet-dump completed ------'
)
def test_dotnet_dump(test_conf: DiagToolsTestConfiguration):
    '''Run sample apps and perform tests.

    '''
    tool_dll_path = dotnet_tool.get_tool_dll(
        'dotnet-dump',
        test_conf.diag_tool_version,
        test_conf.diag_tool_root
    )
    if isinstance(tool_dll_path, Exception):
        return tool_dll_path
        
    webapp_process = target_app.run_webapp(test_conf)
    if isinstance(webapp_process, Exception):
        return webapp_process

    sync_args_list = [
        [test_conf.dotnet_bin_path, tool_dll_path, '--help'],
        [test_conf.dotnet_bin_path, tool_dll_path, 'ps'],
        [test_conf.dotnet_bin_path, tool_dll_path, 'collect', '-p', str(webapp_process.pid)],
    ]
    for args in sync_args_list:
        _, outs, errs = terminal.run_command_sync(
            args,
            cwd=test_conf.test_bed,
            env=test_conf.env,
        )

    webapp_process.terminate()
    while webapp_process.poll() is None:
        time.sleep(1)
    
    # analyze dump with dotnet-dump analyze
    if 'win' in SysInfo.rid:
        dump_path_template = os.path.join(test_conf.test_bed, 'dump*.dmp')
    else:
        dump_path_template = os.path.join(test_conf.test_bed, 'core_*')

    dump_path_candidates = glob.glob(dump_path_template)
    if len(dump_path_candidates) < 1:
        return Exception('no dump file is generated')
    
    dump_path = dump_path_candidates[0]
    analyze_output = os.path.join(test_conf.test_result_folder, 'dump_analyze.log')
    async_args = [test_conf.dotnet_bin_path, tool_dll_path, 'analyze', dump_path]
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
    with open(analyze_output, 'wb+') as fp:
        command, proc = terminal.run_command_async(async_args, stdin=PIPE, stdout=fp, stderr=fp, env=test_conf.env)
        for command in analyze_commands:
            try:
                proc.stdin.write(command)
            except Exception as exception:
                fp.write(f'{exception}\n'.encode('utf-8'))
                continue
        proc.communicate()
        