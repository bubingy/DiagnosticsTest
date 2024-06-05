'''Create, build and run app for CrossOSDAC testing'''

import os
import shutil
from subprocess import Popen
from typing import Union

import app
from tools.sysinfo import SysInfo
from tools import dotnet_app
from tools import terminal
from CrossOSDAC.configuration import RunConfiguration


@app.function_monitor(pre_run_msg='create OOM for CrossOSDAC test.')
def create_oom(test_run_conf: RunConfiguration) -> Union[str, Exception]:
    '''create and build OOM

    :param test_run_conf: test configuration
    :return: path to the project or exception if fail to create
    '''
    # create app
    app_name = f'oom_net{test_run_conf.dotnet_sdk_version}_{SysInfo.rid}'
    app_root = os.path.join(test_run_conf.test_bed, app_name)
    app_root = dotnet_app.create_new_app(test_run_conf.dotnet_bin_path, 'console', app_root, test_run_conf.env)
    if isinstance(app_root, Exception):
        return app_root

    # modify Program.cs
    src_code_path = os.path.join(
        app.script_root,
        'CrossOSDAC',
        'assets',
        'oom',
        'Program.cs'
    )
    dest_code_path = os.path.join(app_root, 'Program.cs')
    try:
        shutil.copy(src_code_path, dest_code_path)
    except Exception as ex:
        return Exception(f'fail to modify oom source code: {ex}')

    # build app 
    app_root = dotnet_app.build_app(test_run_conf.dotnet_bin_path, app_root, test_run_conf.env)
    return app_root


@app.function_monitor(pre_run_msg='run oom for CrossOSDAC test.')
def run_oom(test_run_conf: RunConfiguration) -> Union[Popen, Exception]:
    '''Run oom

    :param test_run_conf: test configuration
    :return: Popen instance or exception if fail to create
    '''
    app_name = f'oom_net{test_run_conf.dotnet_sdk_version}_{SysInfo.rid}'
    app_root = os.path.join(test_run_conf.test_bed, app_name)
    project_bin_path = dotnet_app.get_app_bin(app_name, app_root)
    if isinstance(project_bin_path, Exception):
        return project_bin_path

    env = test_run_conf.env.copy()
    env['COMPlus_DbgEnableMiniDump'] = '1'
    env['COMPlus_DbgMiniDumpType'] = '4'
    env['COMPlus_DbgMiniDumpName'] = os.path.join(
        test_run_conf.dump_folder, f'dump_{app_name}')
    
    command, stdout, stderr = terminal.run_command_sync(
        [project_bin_path],
        cwd=test_run_conf.dump_folder,
        env=env
    )
             
    return command


@app.function_monitor(pre_run_msg='create UHE for CrossOSDAC test.')
def create_uhe(test_run_conf: RunConfiguration) -> Union[str, Exception]:
    '''create and build UHE

    :param test_run_conf: test configuration
    :return: path to the project or exception if fail to create
    '''
    # create app
    app_name = f'uhe_net{test_run_conf.dotnet_sdk_version}_{SysInfo.rid}'
    app_root = os.path.join(test_run_conf.test_bed, app_name)
    app_root = dotnet_app.create_new_app(test_run_conf.dotnet_bin_path, 'console', app_root, test_run_conf.env)
    if isinstance(app_root, Exception):
        return app_root

    # modify Program.cs
    src_code_path = os.path.join(
        app.script_root,
        'CrossOSDAC',
        'assets',
        'uhe',
        'Program.cs'
    )
    dest_code_path = os.path.join(app_root, 'Program.cs')
    try:
        shutil.copy(src_code_path, dest_code_path)
    except Exception as ex:
        return Exception(f'fail to modify uhe source code: {ex}')

    # build app 
    app_root = dotnet_app.build_app(test_run_conf.dotnet_bin_path, app_root, test_run_conf.env)
    return app_root


@app.function_monitor(pre_run_msg='run uhe for CrossOSDAC test.')
def run_uhe(test_run_conf: RunConfiguration) -> Union[Popen, Exception]:
    '''Run oom

    :param test_run_conf: test configuration
    :return: Popen instance or exception if fail to create
    '''
    app_name = f'uhe_net{test_run_conf.dotnet_sdk_version}_{SysInfo.rid}'
    app_root = os.path.join(test_run_conf.test_bed, app_name)
    project_bin_path = dotnet_app.get_app_bin(app_name, app_root)
    if isinstance(project_bin_path, Exception):
        return project_bin_path

    env = test_run_conf.env.copy()
    env['COMPlus_DbgEnableMiniDump'] = '1'
    env['COMPlus_DbgMiniDumpType'] = '4'
    env['COMPlus_DbgMiniDumpName'] = os.path.join(
        test_run_conf.dump_folder, f'dump_{app_name}')
    
    command, stdout, stderr = terminal.run_command_sync(
        [project_bin_path],
        cwd=test_run_conf.dump_folder,
        env=env
    )
             
    return command
