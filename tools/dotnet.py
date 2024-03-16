"""methods for dotnet runtime, sdk and tools installation"""

import os
from urllib import request

import app
from tools.terminal import run_command_sync


@app.check_function_input()
@app.log_function(
    pre_run_msg='start to download dotnet-install script',
    post_run_msg='download dotnet-install script completed')
def donwload_install_script(rid: str, script_path: str) -> str|Exception:
    """download dotnet-install script
    
    :param rid: .NET rid
    :param script_path: path to dotnet-install script
    :return: path to dotnet-install script or Exception if fail to download
    """
    if 'win' in rid:
        script_download_link = 'https://dotnet.microsoft.com/download/dotnet/scripts/v1/dotnet-install.ps1'

    else:
        script_download_link = 'https://dotnet.microsoft.com/download/dotnet/scripts/v1/dotnet-install.sh'

    try:
        req = request.urlopen(script_download_link)
        with open(script_path, 'wb+') as f:
            f.write(req.read())
        return script_path
    except Exception as ex:
        return Exception(f'fail to download dotnet-install script: {ex}')


@app.check_function_input()
@app.log_function(
    pre_run_msg='start to make script runnable on non-windows platforms',
    post_run_msg='making script runnable on non-windows platforms completed')
def enable_runnable(rid: str, script_path: str) -> str|Exception:
    """make script runnable on non-windows platforms
    
    :param rid: .NET rid
    :param script_path: path to script
    :return: path to script or Exception if fail
    """
    if 'win' in rid:
        return script_path
    
    command, stdout, stderr = run_command_sync(['chmod', '+x', script_path])
    if stderr != '':
        return Exception(f'fail to make script runnable, see log for details')
    else:
        return script_path


@app.check_function_input()
@app.log_function(
    pre_run_msg='start to install sdk with dotnet-install script',
    post_run_msg='install sdk with dotnet-install script completed')
def install_sdk_from_script(rid: str,
                            script_path: str,
                            sdk_version: str, 
                            dotnet_root: os.PathLike,
                            arch: str=None) -> str|Exception:
    """install sdk with dotnet-install script
    
    :param rid: .NET rid
    :param script_path: path to dotnet-install script
    :param sdk_version: version of .NET sdk
    :param dotnet_root: root of dotnet executable
    :param arch: cpu type
    :return: DOTNET_ROOT or Exception if fail to install
    """
    if 'win' in rid:
        script_engine = 'powershell.exe'
    elif 'osx' in rid:
        script_engine = '/bin/zsh'
    else:
        script_engine = '/bin/bash'

    if arch is not None:
        args = [script_engine, script_path, '-InstallDir', dotnet_root, '-v', sdk_version, '-Architecture', arch]
    else:
        args = [script_engine, script_path, '-InstallDir', dotnet_root, '-v', sdk_version]
    
    command, stdout, stderr = run_command_sync(args)
    if stderr != '':
        return Exception(f'fail to install sdk {sdk_version}, see log for details')
    else:
        return dotnet_root

# TODO
# @app.log_function()
# def install_runtime_from_script(runtime_type: str, 
#                                 runtime_version: str, 
#                                 test_bed: os.PathLike, 
#                                 dotnet_root: os.PathLike, 
#                                 rid: str, 
#                                 arch: str=None,
#                                 logger: ScriptLogger=None):
#     logger.info(f'download dotnet install script')
#     if 'win' in rid:
#         script_download_link = 'https://dot.net/v1/dotnet-install.ps1'
#         script_engine = 'powershell.exe'

#     else:
#         script_download_link = 'https://dotnet.microsoft.com/download/dotnet/scripts/v1/dotnet-install.sh'
#         script_engine = '/bin/bash'

#     script_path = os.path.join(test_bed, os.path.basename(script_download_link))
#     req = request.urlopen(script_download_link)
#     with open(script_path, 'w+') as f:
#         f.write(req.read().decode())

#     if 'win' not in rid:
#         run_command_sync(f'chmod +x {script_path}')

#     if arch is not None:
#         command = f'{script_engine} {script_path} -InstallDir {dotnet_root} -v {runtime_version} --runtime {runtime_type} -Architecture {arch}'
#     else:
#         command = f'{script_engine} {script_path} -InstallDir {dotnet_root} -v {runtime_version} --runtime {runtime_type}'
    
#     outs, errs = run_command_sync(command, stdout=PIPE, stderr=PIPE)
#     logger.info(f'run command:\n{command}\n{outs}')
    
#     if errs != '':
#         logger.error(f'fail to install .net runtime {runtime_version}!\n{errs}')
#         exit(-1)
    

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


@app.check_function_input(
    pre_run_msg='start to download perfcollect script',
    post_run_msg='download perfcollect script completed')
@app.log_function()
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