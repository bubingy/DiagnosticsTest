'''Create, build and run app for diag tools testing'''

import os
import time
import shutil
from subprocess import Popen
from typing import Union

import app
from tools import dotnet_app
from tools import terminal
from DiagnosticTools.configuration import DiagToolsTestConfiguration



@app.function_monitor(pre_run_msg='create and build console app for diag tool test.')
def create_build_console_app(test_conf: DiagToolsTestConfiguration) -> Union[str, Exception]:
    '''create and build console app

    :param test_conf: test configuration
    :return: path to the project or exception if fail to create
    '''
    # create app
    app_root = os.path.join(test_conf.test_bed, 'console')
    app_root = dotnet_app.create_new_app(test_conf.dotnet_bin_path, 'console', app_root, test_conf.env)
    if isinstance(app_root, Exception):
        return app_root

    # modify Program.cs
    src_code_path = os.path.join(
        app.script_root,
        'DiagnosticTools',
        'assets',
        'consoleapp',
        'Program.cs'
    )
    dest_code_path = os.path.join(app_root, 'Program.cs')
    try:
        shutil.copy(src_code_path, dest_code_path)
    except Exception as ex:
        return Exception(f'fail to modify console app source code: {ex}')

    # build app 
    app_root = dotnet_app.build_app(test_conf.dotnet_bin_path, app_root, test_conf.env)
    return app_root


@app.function_monitor(pre_run_msg='create and build webapp for diag tool test.')
def create_build_webapp(test_conf: DiagToolsTestConfiguration) -> Union[str, Exception]:
    '''create and build webapp

    :param test_conf: test configuration
    :return: path to the project or exception if fail to create
    '''
    # create app
    app_root = os.path.join(test_conf.test_bed, 'webapp')
    app_root = dotnet_app.create_new_app(test_conf.dotnet_bin_path, 'webapp', app_root, test_conf.env)

    # build app 
    app_root = dotnet_app.build_app(test_conf.dotnet_bin_path, app_root, test_conf.env)
    return app_root


@app.function_monitor(pre_run_msg='run webapp for diag tool test.')
def run_webapp(test_conf: DiagToolsTestConfiguration) -> Union[Popen, Exception]:
    '''Run webapp

    :param test_conf: test configuration
    :return: Popen instance or exception if fail to create
    '''
    app_root = os.path.join(test_conf.test_bed, 'webapp')
    project_bin_path = dotnet_app.get_app_bin('webapp', app_root)
    if isinstance(project_bin_path, Exception):
        return project_bin_path

    tmp_path = os.path.join(app_root, 'tmp')
    with open (tmp_path, 'w+') as tmp_write:
        command, proc = terminal.run_command_async(
            project_bin_path,
            stdout=tmp_write,
            env=test_conf.env
        )
    with open(tmp_path, 'r') as tmp_read:
        while True:
            if 'Application started' in tmp_read.read():
                print('webapp is running!')
                tmp_read.close()
                break
            else:
                time.sleep(2)
                
    return proc


@app.function_monitor(pre_run_msg='create GCDumpPlayground2 for diag tool test.')
def create_build_gc_dump_playground2(test_conf: DiagToolsTestConfiguration) -> Union[str, Exception]:
    '''create and build GCDumpPlayground2

    :param test_conf: test configuration
    :return: path to the project or exception if fail to create
    '''
    # create app
    app_root = os.path.join(test_conf.test_bed, 'GCDumpPlayground2')
    app_root = dotnet_app.create_new_app(test_conf.dotnet_bin_path, 'console', app_root, test_conf.env)
    if isinstance(app_root, Exception):
        return app_root

    # modify Program.cs
    src_code_path = os.path.join(
        app.script_root,
        'DiagnosticTools',
        'assets',
        'GCDumpPlayground2',
        'Program.cs'
    )
    dest_code_path = os.path.join(app_root, 'Program.cs')
    try:
        shutil.copy(src_code_path, dest_code_path)
    except Exception as ex:
        return Exception(f'fail to modify GCDumpPlayground2 source code: {ex}')

    # build app 
    app_root = dotnet_app.build_app(test_conf.dotnet_bin_path, app_root, test_conf.env)
    return app_root


@app.function_monitor(pre_run_msg='run GCDumpPlayground2 for diag tool test.')
def run_gc_dump_playground2(test_conf: DiagToolsTestConfiguration) -> Union[Popen, Exception]:
    '''Run GCDumpPlayground2

    :param test_conf: test configuration
    :return: Popen instance or exception if fail to create
    '''
    app_root = os.path.join(test_conf.test_bed, 'GCDumpPlayground2')
    project_bin_path = dotnet_app.get_app_bin('GCDumpPlayground2', app_root)
    if isinstance(project_bin_path, Exception):
        return project_bin_path

    tmp_path = os.path.join(app_root, 'tmp')
    with open (tmp_path, 'w+') as tmp_write:
        command, proc = terminal.run_command_async(
            [project_bin_path, '0.05'],
            stdout=tmp_write,
            env=test_conf.env
        )
        
    with open(tmp_path, 'r') as tmp_read:
        while True:
            if 'Pause for gcdumps.' in tmp_read.read():
                print('GCDumpPlayground2 is running!')
                tmp_read.close()
                break
            else:
                time.sleep(2)
                
    return proc