from __future__ import annotations
import os
import shutil

import app
from app import AppLogger
from tools import sdk_runtime
from tools import dotnet_tool
from tools import terminal
from tools.sysinfo import SysInfo
from LTTng import target_app
from LTTng.configuration import LTTngTestConfiguration, RunConfiguration


def init_test(test_conf: LTTngTestConfiguration) -> None:
    '''Create testbed folder
    
    :param test_conf: LTTngTestConfiguration instance
    '''
    # step 1. create testbed and test result folder 
    os.makedirs(test_conf.test_bed, exist_ok=True)
    os.makedirs(test_conf.test_result_folder, exist_ok=True)

    # step 2. copy configuration file to test result folder
    shutil.copy(test_conf.conf_file_path, test_conf.test_result_folder)

    # step 3. download perfcollect
    perfcollect_path = os.path.join(test_conf.test_bed, 'perfcollect')
    dotnet_tool.download_perfcollect(perfcollect_path)

    # step 4. create env script
    for run_conf in test_conf.run_conf_list:
        if 'win' in SysInfo.rid:
            env_script_path = os.path.join(test_conf.test_bed, f'env_script_net{run_conf.dotnet_sdk_version}.ps1')
            lines = [
                f'$Env:DOTNET_ROOT={run_conf.dotnet_root}\n',
                f'$Env:Path+=;{run_conf.dotnet_root}\n'
            ]
        else:
            env_script_path = os.path.join(test_conf.test_bed, f'env_script_net{run_conf.dotnet_sdk_version}.sh')
            lines = [
                f'export DOTNET_ROOT={run_conf.dotnet_root}\n',
                f'export PATH=$PATH:{run_conf.dotnet_root}\n'
            ]
        
        with open(env_script_path, 'w+') as fp:
            fp.writelines(lines)


def install_DotNET_SDK(run_conf: RunConfiguration) -> None|Exception:
    '''Download install script and install SDK
    
    :param test_conf: RunConfiguration instance
    '''
    log_file_path = os.path.join(run_conf.test_result_folder, 'sdk_install.log')
    app.logger = AppLogger('.NET Installation', log_file_path)

    if 'win' in SysInfo.rid:
        script_path = os.path.join(run_conf.test_bed, 'dotnet_install.ps1')
    else:
        script_path = os.path.join(run_conf.test_bed, 'dotnet_install.sh')
    script_path = sdk_runtime.donwload_install_script(SysInfo.rid, script_path)
    script_path = sdk_runtime.enable_runnable(SysInfo.rid, script_path)

    dotnet_root = sdk_runtime.install_sdk_from_script(
        SysInfo.rid, script_path, run_conf.dotnet_sdk_version, run_conf.dotnet_root)
    

def prepare_sample_app(run_conf: RunConfiguration) -> None|Exception:
    '''Create and build some .NET app for testing
    
    :param test_conf: DiagToolsTestConfiguration instance
    '''
    log_file_path = os.path.join(run_conf.test_result_folder, 'dotnet_app.log')
    app.logger = AppLogger('.NET app Create and Build', log_file_path)

    try:
        target_app.create_gcperfsim(run_conf)
    except Exception as ex:
        app.logger.error(f'fail to create gcperfsim: {ex}')


def clean_temp(run_conf: RunConfiguration) -> None|Exception:
    if 'win' in SysInfo.rid: home_path = os.environ['USERPROFILE']
    else: home_path = os.environ['HOME']

    temp_file_folder_list = [
        os.path.join(home_path, '.aspnet'),
        os.path.join(home_path, '.debug'),
        os.path.join(home_path, '.dotnet'),
        os.path.join(home_path, '.nuget'),
        os.path.join(home_path, '.templateengine'),
        os.path.join(home_path, '.lldb'),
        os.path.join(home_path, '.lldbinit'),
        os.path.join(home_path, 'lttng-traces'),
        os.path.join(home_path, '.local')
    ]
    temp_files_folders_collection_path = os.path.join(run_conf.test_bed, f'temp_files_folders_net{run_conf.dotnet_sdk_version}')
    os.makedirs(temp_files_folders_collection_path, exist_ok=True)
    for temp in temp_file_folder_list:
        if not os.path.exists(temp):
            continue
        try:
            shutil.move(temp, temp_files_folders_collection_path)
        except Exception as e:
            print(f'fail to remove {temp}: {e}')


def run_test_for_single_SDK(run_conf: RunConfiguration) -> None|Exception:
    log_file_path = os.path.join(run_conf.test_result_folder, 'lttng.log')
    app.logger = AppLogger('Run LTTng test', log_file_path)

    gcperfsim_process = target_app.run_gcperfsim(run_conf)
    if isinstance(gcperfsim_process, Exception):
        return gcperfsim_process

    trace_path = os.path.join(
        run_conf.test_result_folder,
        f'trace_net{run_conf.dotnet_sdk_version}_{SysInfo.rid}'
    )

    perfcollect_path = perfcollect_path = os.path.join(run_conf.test_bed, 'perfcollect')
    args = [
        '/bin/bash', perfcollect_path, 'collect', trace_path, '-collectsec', '30'
    ]
    terminal.run_command_sync(args, cwd=run_conf.test_result_folder, env=run_conf.env)