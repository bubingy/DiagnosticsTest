'''methods for dotnet tool installation'''

import glob
from typing import Union
from urllib import request

import app
from tools.terminal import run_command_sync


@app.function_monitor()
def install_tool(dotnet_bin_path: str, 
                 tool: str, 
                 tool_root: str, 
                 tool_version: str, 
                 tool_feed: str,
                 env: dict) -> Union[str, Exception]:
    '''Install dotnet tool
    
    :param dotnet_bin_path: path to dotnet executable
    :param tool: name of tool
    :param tool_root: parent dir of the tool
    :param tool_version: version of tool
    :param tool_feed: feed of tool
    :param env: required environment variable
    :return: parent dir of the tool or exception if fail to install
    '''
    args = [
        dotnet_bin_path, 'tool', 'install', tool,
        '--tool-path', tool_root,
        '--version', tool_version,
        '--add-source', tool_feed
    ]
    command, stdout, stderr = run_command_sync(args, env=env)
    if stderr != '':
        return Exception(f'fail to install {tool}, see log for details')
    else:
        return tool_root


@app.function_monitor(
    pre_run_msg='start to download perfcollect script',
    post_run_msg='download perfcollect script completed')
def download_perfcollect(perfcollect_path: str) -> Union[str, Exception]:
    '''Download perfcollect script

    :param perfcollect_path: path to perfcollect script
    '''
    try:
        req = request.urlopen(
            'https://raw.githubusercontent.com/microsoft/perfview/main/src/perfcollect/perfcollect'
        )
        with open(perfcollect_path, 'w+') as f:
            f.write(req.read().decode())
        return perfcollect_path
    except Exception as ex:
        return Exception(f'fail to download perfcollect script: {ex}')
    

def get_tool_dll(tool_name, tool_version, tool_root: str) -> Union[str, Exception]:
    '''Get path of executable file

    :param tool_name: name of diag tool
    :param tool_root: root of diag tools
    :return: path of executable file or exception if fail to create
    '''
    tool_dll_path_template = (
        f'{tool_root}/.store/{tool_name}'
        f'/{tool_version}/{tool_name}'
        f'/{tool_version}/tools/*/any/{tool_name}.dll'
    )
    tool_dll_path_candidates = glob.glob(tool_dll_path_template)
    
    if len(tool_dll_path_candidates) < 1:
        return Exception(f'no dll file availble for {tool_name}')
    return tool_dll_path_candidates[0]