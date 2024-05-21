import os
import shutil
from __future__ import annotations

import app
from app import AppLogger
from tools import sdk_runtime
from tools import dotnet_tool
from tools.sysinfo import SysInfo
from DiagnosticTools import target_app
from DiagnosticTools.configuration import DiagToolsTestConfiguration
from DiagnosticTools import dotnet_counters
from DiagnosticTools import dotnet_dump
from DiagnosticTools import dotnet_gcdump
from DiagnosticTools import dotnet_sos
from DiagnosticTools import dotnet_stack
from DiagnosticTools import dotnet_trace


def init_test(test_conf: DiagToolsTestConfiguration) -> None:
    '''Create testbed folder
    
    :param test_conf: DiagToolsTestConfiguration instance
    '''
    # step 1. create testbed and test result folder 
    os.makedirs(test_conf.test_bed, exist_ok=True)
    os.makedirs(test_conf.test_result_folder, exist_ok=True)

    # step 2. copy configuration file to test result folder
    shutil.copy(test_conf.conf_file_path, test_conf.test_result_folder)

    # step 3. create env script
    if 'win' in SysInfo.rid:
        env_script_path = os.path.join(test_conf.test_bed, 'env_script.ps1')
        lines = [
            f'$Env:DOTNET_ROOT={test_conf.dotnet_root}\n',
            f'$Env:Path+=;{test_conf.dotnet_root}\n',
            f'$Env:Path+=;{test_conf.diag_tool_root}\n'
        ]
    else:
        env_script_path = os.path.join(test_conf.test_bed, 'env_script.sh')
        lines = [
            f'export DOTNET_ROOT={test_conf.dotnet_root}\n',
            f'export PATH=$PATH:{test_conf.dotnet_root}\n',
            f'export PATH=$PATH:{test_conf.diag_tool_root}\n'
        ]
    
    with open(env_script_path, 'w+') as fp:
        fp.writelines(lines)


def install_DotNET_SDK(test_conf: DiagToolsTestConfiguration) -> None|Exception:
    '''Download install script and install SDK
    
    :param test_conf: DiagToolsTestConfiguration instance
    '''
    log_file_path = os.path.join(test_conf.test_result_folder, 'sdk_install.log')
    app.logger = AppLogger('.NET Installation', log_file_path)

    if 'win' in SysInfo.rid:
        script_path = os.path.join(test_conf.test_bed, 'dotnet_install.ps1')
    else:
        script_path = os.path.join(test_conf.test_bed, 'dotnet_install.sh')
    script_path = sdk_runtime.donwload_install_script(SysInfo.rid, script_path)
    script_path = sdk_runtime.enable_runnable(SysInfo.rid, script_path)

    dotnet_root = sdk_runtime.install_sdk_from_script(
        SysInfo.rid, script_path, test_conf.dotnet_sdk_version, test_conf.dotnet_root)


def install_diagnostic_tools(test_conf: DiagToolsTestConfiguration) -> None|Exception:
    '''Install diagnostic tools
    
    :param test_conf: DiagToolsTestConfiguration instance
    '''
    log_file_path = os.path.join(test_conf.test_result_folder, 'tool_install.log')
    app.logger = AppLogger('Tools Installation', log_file_path)

    for tool_name in test_conf.diag_tool_to_install:
        try:
            dotnet_tool.install_tool(
                test_conf.dotnet_bin_path,
                tool_name,
                test_conf.diag_tool_root,
                test_conf.diag_tool_version,
                test_conf.diag_tool_feed,
                test_conf.env)

        except Exception as ex:
            app.logger.error(f'fail to install tool {tool_name}: {ex}')
            continue


def prepare_sample_app(test_conf: DiagToolsTestConfiguration) -> None|Exception:
    '''Create and build some .NET app for testing
    
    :param test_conf: DiagToolsTestConfiguration instance
    '''
    log_file_path = os.path.join(test_conf.test_result_folder, 'dotnet_app.log')
    app.logger = AppLogger('.NET app Create and Build', log_file_path)

    for app_name in test_conf.app_to_create:
        try:
            if app_name == 'webapp':
                target_app.create_build_webapp(test_conf)
            elif app_name == 'console':
                target_app.create_build_console_app(test_conf)
            elif app_name == 'GCDumpPlayground2':
                target_app.create_build_gc_dump_playground2(test_conf)
            else:
                print(f'unknown app {app_name}')
        except Exception as ex:
            app.logger.error(f'fail to create {app_name}: {ex}')
            continue


def clean_temp(test_conf: DiagToolsTestConfiguration) -> None|Exception:
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
    temp_files_folders_collection_path = os.path.join(test_conf.test_bed, 'temp_files_folders')
    os.makedirs(temp_files_folders_collection_path, exist_ok=True)
    for temp in temp_file_folder_list:
        if not os.path.exists(temp):
            continue
        try:
            shutil.move(temp, temp_files_folders_collection_path)
        except Exception as e:
            print(f'fail to remove {temp}: {e}')


def restore_temp(test_conf: DiagToolsTestConfiguration) -> None|Exception:
    if 'win' in SysInfo.rid: home_path = os.environ['USERPROFILE']
    else: home_path = os.environ['HOME']

    temp_files_folders_collection_path = os.path.join(test_conf.test_bed, 'temp_files_folders')
    for temp_file_folder_name in os.listdir(temp_files_folders_collection_path):
        temp_file_folder = os.path.join(test_conf.test_bed, temp_file_folder_name)
        try:
            shutil.move(temp_file_folder, home_path)
        except Exception as e:
            print(f'fail to retore {temp_file_folder}: {e}')


def run_test(test_conf: DiagToolsTestConfiguration) -> None|Exception:
    tool_name_runner_map = {
        'dotnet-counters': dotnet_counters.test_dotnet_counters,
        'dotnet-dump': dotnet_dump.test_dotnet_dump,
        'dotnet-gcdump': dotnet_gcdump.test_dotnet_gcdump,
        'dotnet-sos': dotnet_sos.test_dotnet_sos,
        'dotnet-stack': dotnet_stack.test_dotnet_stack,
        'dotnet-trace': dotnet_trace.test_dotnet_trace
    }
    for tool_name in test_conf.diag_tool_to_test:
        log_file_path = os.path.join(test_conf.test_result_folder, f'{tool_name}.log')
        app.logger = AppLogger(f'test {tool_name}', log_file_path)
        runner = tool_name_runner_map[tool_name]
        runner(test_conf)
