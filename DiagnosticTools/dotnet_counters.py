import os
import time

import app
from tools import dotnet_tool
from tools import terminal
from DiagnosticTools.configuration import DiagToolsTestConfiguration
from DiagnosticTools import target_app


@app.function_monitor(
    pre_run_msg='------ start to test dotnet-counters ------',
    post_run_msg='------ test dotnet-counters completed ------'
)
def test_dotnet_counters(test_conf: DiagToolsTestConfiguration):
    '''Run sample apps and perform tests.

    '''
    tool_dll_path = dotnet_tool.get_tool_dll(
        'dotnet-counters',
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
        [test_conf.dotnet_bin_path, tool_dll_path, 'list'],
        [test_conf.dotnet_bin_path, tool_dll_path, 'ps'],
    ]
    for args in sync_args_list:
        _, outs, errs = terminal.run_command_sync(
            args,
            cwd=test_conf.test_result_folder,
            env=test_conf.env,
        )

    async_args_list = [
        [test_conf.dotnet_bin_path, tool_dll_path, 'collect', '-p', str(webapp_process.pid), '-o', 'webapp_counter.csv'],
        [test_conf.dotnet_bin_path, tool_dll_path, 'monitor', '-p', str(webapp_process.pid)],
    ]
    for args in async_args_list:
        _, p = terminal.run_command_async(
            args,
            cwd=test_conf.test_result_folder,
            env=test_conf.env
        )
        time.sleep(10)
        p.terminate()
        p.communicate()
        time.sleep(3)

    webapp_process.terminate()
    webapp_process.communicate()
    
    console_app_root = os.path.join(test_conf.test_bed, 'console')
    console_app_bin = target_app.get_app_bin('console', console_app_root)
    if isinstance(console_app_bin, Exception):
        return console_app_bin
    
    async_args_list = [
        [test_conf.dotnet_bin_path, tool_dll_path, 'collect', '--', console_app_bin, '-o', 'console_counter.csv'],
        [test_conf.dotnet_bin_path, tool_dll_path, 'monitor', '--', console_app_bin],
    ]
    for args in async_args_list:
        command, p = terminal.run_command_async(
            args,
            cwd=test_conf.test_result_folder,
            env=test_conf.env,
        )
        p.communicate()
        time.sleep(3)