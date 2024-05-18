import os
import time

import app
from tools import dotnet_tool
from tools import terminal
from DiagnosticTools.configuration import DiagToolsTestConfiguration
from DiagnosticTools import target_app


@app.function_monitor(
    pre_run_msg='------ start to test dotnet-stack ------',
    post_run_msg='------ test dotnet-stack completed ------'
)
def test_dotnet_stack(test_conf: DiagToolsTestConfiguration):
    '''Run sample apps and perform tests.

    '''
    tool_dll_path = dotnet_tool.get_tool_dll(
        'dotnet-stack',
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
        [test_conf.dotnet_bin_path, tool_dll_path, 'report', '-p', str(webapp_process.pid)],
    ]
    for args in sync_args_list:
        _, outs, errs = terminal.run_command_sync(
            args,
            cwd=test_conf.test_result_folder,
            env=test_conf.env,
        )

    webapp_process.terminate()
    while webapp_process.poll() is None:
        time.sleep(1)