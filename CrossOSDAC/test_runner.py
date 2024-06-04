from __future__ import annotations
import os
import shutil

import app
from app import AppLogger
from tools import sdk_runtime
from tools import dotnet_tool
from tools import terminal
from tools.sysinfo import SysInfo
from CrossOSDAC import target_app
from CrossOSDAC import dump_analyzer
from CrossOSDAC.configuration import CrossOSDACConfiguration, RunConfiguration


def init_test(test_conf: CrossOSDACConfiguration) -> None:
    '''Create testbed folder
    
    :param test_conf: LTTngTestConfiguration instance
    '''
    # step 1. create testbed
    if 'win' in SysInfo.rid:
        testbed = test_conf.validate_testbed
    else:
        testbed = test_conf.analyze_testbed
        os.makedirs(testbed, exist_ok=True)

    # step 2. copy configuration file to test result folder
    shutil.copy(test_conf.conf_file_path, testbed)

    # step 3. create env script, dump folders and dump analyze folders
    for run_conf in test_conf.run_conf_list:
        if 'win' in SysInfo.rid:
            env_script_path = os.path.join(testbed, f'env_script_net{run_conf.dotnet_sdk_version}.ps1')
            lines = [
                f'$Env:DOTNET_ROOT={run_conf.dotnet_root}\n',
                f'$Env:Path+=;{run_conf.dotnet_root}\n',
                f'$Env:Path+=;{run_conf.diag_tool_root}\n'
            ]
        else:
            env_script_path = os.path.join(testbed, f'env_script_net{run_conf.dotnet_sdk_version}.sh')
            lines = [
                f'export DOTNET_ROOT={run_conf.dotnet_root}\n',
                f'export PATH=$PATH:{run_conf.dotnet_root}\n',
                f'$Env:Path+=;{run_conf.diag_tool_root}\n'
            ]
            
            os.makedirs(run_conf.dump_folder, exist_ok=True)
            os.makedirs(run_conf.analyze_folder, exist_ok=True)
        
        with open(env_script_path, 'w+') as fp:
            fp.writelines(lines)


def install_DotNET_SDK(run_conf: RunConfiguration) -> None|Exception:
    '''Download install script and install SDK
    
    :param test_conf: RunConfiguration instance
    '''
    log_file_path = os.path.join(run_conf.test_bed, 'sdk_install.log')
    app.logger = AppLogger('.NET Installation', log_file_path)

    if 'win' in SysInfo.rid:
        script_path = os.path.join(run_conf.test_bed, 'dotnet_install.ps1')
    else:
        script_path = os.path.join(run_conf.test_bed, 'dotnet_install.sh')
    script_path = sdk_runtime.donwload_install_script(SysInfo.rid, script_path)
    script_path = sdk_runtime.enable_runnable(SysInfo.rid, script_path)

    dotnet_root = sdk_runtime.install_sdk_from_script(
        SysInfo.rid, script_path, run_conf.dotnet_sdk_version, run_conf.dotnet_root, run_conf.arch)
    

def install_dotnet_dump(run_conf: RunConfiguration) -> None|Exception:
    dotnet_tool.install_tool(
        run_conf.dotnet_bin_path,
        'dotnet-dump',
        run_conf.diag_tool_root,
        run_conf.diag_tool_version,
        run_conf.diag_tool_feed,
        run_conf.env
    )


def prepare_sample_app(run_conf: RunConfiguration) -> None|Exception:
    '''Create and build some .NET app for testing
    
    :param test_conf: DiagToolsTestConfiguration instance
    '''
    log_file_path = os.path.join(run_conf.test_bed, 'dotnet_app.log')
    app.logger = AppLogger('.NET app Create and Build', log_file_path)

    try:
        target_app.create_oom(run_conf)
    except Exception as ex:
        app.logger.error(f'fail to create oom: {ex}')

    
    try:
        target_app.create_uhe(run_conf)
    except Exception as ex:
        app.logger.error(f'fail to create uhe: {ex}')


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
    log_file_path = os.path.join(run_conf.test_bed, f'CrossOSDAC-{run_conf.dotnet_sdk_version}.log')
    app.logger = AppLogger('Run CrossOSDAC test', log_file_path)

    # generate dumps, linux only
    if 'win' not in SysInfo.rid:
        target_app.run_oom(run_conf)
        target_app.run_uhe(run_conf)

    # analyze dump
    dump_analyzer.analyze_dump(run_conf)
