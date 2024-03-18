"""methods for dotnet tool installation"""

from urllib import request

import app
from tools.terminal import run_command_sync


@app.check_function_input()
@app.log_function()
def install_tool(dotnet_bin_path: str, 
                 tool: str, 
                 tool_root: str, 
                 tool_version: str, 
                 tool_feed: str,
                 env: dict) -> str|Exception:
    """Install dotnet tool
    
    :param dotnet_bin_path: path to dotnet executable
    :param tool: name of tool
    :param tool_root: parent dir of the tool
    :param tool_version: version of tool
    :param tool_feed: feed of tool
    :param env: required environment variable
    :return: parent dir of the tool or exception if fail to install
    """
    args = [
        dotnet_bin_path, 'tool', 'install', tool,
        '--tool-path', tool_root,
        '--version', tool_version,
        '--add-source', tool_feed
    ]
    command, stdout, stderr = run_command_sync(args, env=env)
    if stderr != '':
        return Exception(f'fail to install tool, see log for details')
    else:
        return tool_root


@app.check_function_input()
@app.log_function(
    pre_run_msg='start to download perfcollect script',
    post_run_msg='download perfcollect script completed')
def download_perfcollect(perfcollect_path: str):
    """Download perfcollect script

    :param perfcollect_path: path to perfcollect script
    """
    try:
        req = request.urlopen(
            'https://raw.githubusercontent.com/microsoft/perfview/main/src/perfcollect/perfcollect'
        )
        with open(perfcollect_path, 'w+') as f:
            f.write(req.read().decode())
        return perfcollect_path
    except Exception as ex:
        return Exception(f'fail to download perfcollect script: {ex}')
    
