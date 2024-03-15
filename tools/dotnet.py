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
        return ex


@app.check_function_input()
@app.log_function(
    pre_run_msg='start to make dotnet-install script runnable on non-windows platforms',
    post_run_msg='making dotnet-install script runnable on non-windows platforms completed')
def enable_runnable(rid: str, script_path: str) -> str|Exception:
    """make dotnet-install script runnable on non-windows platforms
    
    :param rid: .NET rid
    :param script_path: path to dotnet-install script
    :return: path to dotnet-install script or Exception if fail
    """
    if 'win' in rid:
        return script_path
    
    command, stdout, stderr = run_command_sync(['chmod', '+x', script_path])
    if stderr != '':
        return Exception(f'fail to make dotnet-install script runnable, see log for details')
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
    else:
        script_engine = '/bin/bash'

    if arch is not None:
        args = [script_engine, script_path, '-InstallDir', dotnet_root, '-v', sdk_version, '-Architecture', arch]
    else:
        args = [script_engine, script_path, '-InstallDir', dotnet_root, '-v', sdk_version]
    
    command, stdout, stderr = run_command_sync(args)
    if stderr != '':
        return Exception(f'fail to make dotnet-install script runnable, see log for details')
    

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
