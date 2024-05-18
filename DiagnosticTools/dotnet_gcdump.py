import time

import app
from tools import dotnet_tool
from tools import terminal
from DiagnosticTools.configuration import DiagToolsTestConfiguration
from DiagnosticTools import target_app


@app.function_monitor(
    pre_run_msg='------ start to test dotnet-gcdump ------',
    post_run_msg='------ test dotnet-gcdump completed ------'
)
def test_dotnet_gcdump(test_conf: DiagToolsTestConfiguration):
    '''Run sample apps and perform tests.

    '''
    tool_dll_path = dotnet_tool.get_tool_dll(
        'dotnet-gcdump',
        test_conf.diag_tool_version,
        test_conf.diag_tool_root
    )
    if isinstance(tool_dll_path, Exception):
        return tool_dll_path
        
    gcdump_playground_process = target_app.run_gc_dump_playground2(test_conf)
    if isinstance(gcdump_playground_process, Exception):
        return gcdump_playground_process

    sync_args_list = [
        [test_conf.dotnet_bin_path, tool_dll_path, '--help'],
        [test_conf.dotnet_bin_path, tool_dll_path, 'ps'],
        [test_conf.dotnet_bin_path, tool_dll_path, 'collect', '-p', str(gcdump_playground_process.pid), '-v'],
    ]
    for args in sync_args_list:
        _, outs, errs = terminal.run_command_sync(
            args,
            cwd=test_conf.test_result_folder,
            env=test_conf.env,
        )

    gcdump_playground_process.terminate()
    while gcdump_playground_process.poll() is None:
        time.sleep(1)