''''''

from __future__ import annotations
import os
import shutil
from subprocess import Popen

import app
from tools import dotnet_app
from tools import terminal
from LTTng.configuration import RunConfiguration 


@app.function_monitor(pre_run_msg='create GCPerfsim for lttng test.')
def create_gcperfsim(test_run_conf: RunConfiguration) -> str | Exception:
    '''create and build GCPerfsim

    :param test_run_conf: test configuration
    :return: path to the project or exception if fail to create
    '''
    # create app
    app_root = os.path.join(test_run_conf.test_bed, f'gcperfsim_net{test_run_conf.dotnet_sdk_version}')
    app_root = dotnet_app.create_new_app(test_run_conf.dotnet_bin_path, 'console', app_root, test_run_conf.env)
    if isinstance(app_root, Exception):
        return app_root

    # modify Program.cs
    src_code_path = os.path.join(
        app.script_root,
        'LTTng',
        'assets',
        'gcperfsim',
        'Program.cs'
    )
    dest_code_path = os.path.join(app_root, 'Program.cs')
    try:
        shutil.copy(src_code_path, dest_code_path)
    except Exception as ex:
        return Exception(f'fail to modify gcperfsim source code: {ex}')

    # build app 
    app_root = dotnet_app.build_app(test_run_conf.dotnet_bin_path, app_root, test_run_conf.env)
    return app_root


@app.function_monitor(pre_run_msg='run gcperfsim for diag tool test.')
def run_gcperfsim(test_run_conf: RunConfiguration) -> Popen | Exception:
    '''Run gcperfsim

    :param test_run_conf: test configuration
    :return: Popen instance or exception if fail to create
    '''
    app_root = os.path.join(test_run_conf.test_bed, 'gcperfsim')
    project_bin_path = dotnet_app.get_app_bin('gcperfsim', app_root)
    if isinstance(project_bin_path, Exception):
        return project_bin_path

    env = test_run_conf.env.copy()
    env['COMPlus_PerfMapEnabled'] = '1'
    env['COMPlus_EnableEventLog'] = '1'
    
    command, proc = terminal.run_command_async(
        [project_bin_path],
        cwd=test_run_conf.test_result_folder,
        env=env
    )
             
    return proc