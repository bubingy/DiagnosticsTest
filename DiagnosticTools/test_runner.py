import os

import app
from app import AppLogger
from DiagnosticTools import target_app
from DiagnosticTools.configuration import DiagToolsTestConfiguration
from tools import sdk_runtime
from tools import dotnet_tool
from tools.sysinfo import SysInfo


def pre_run(test_conf: DiagToolsTestConfiguration) -> dict|Exception:
    """Initialization of test
    
    :param test_conf: DiagToolsTestConfiguration instance
    """
    # step 0. create testbed and test result folder 
    os.makedirs(test_conf.test_bed, exist_ok=True)
    os.makedirs(test_conf.test_result_folder, exist_ok=True)

    # step 1. install .NET SDK
    log_file_path = os.path.join(test_conf.test_result_folder, 'sdk_install.log')
    app.logger = AppLogger('.NET Installation', log_file_path)

    script_path = os.path.join(test_conf.test_bed, 'dotnet_install')
    script_path = sdk_runtime.donwload_install_script(SysInfo.rid, script_path)
    script_path = sdk_runtime.enable_runnable(SysInfo.rid, script_path)

    dotnet_root = sdk_runtime.install_sdk_from_script(
        SysInfo.rid, script_path, test_conf.dotnet_sdk_version, test_conf.dotnet_root)
    
    if isinstance(dotnet_root, Exception): 
        return dotnet_root
    
    # step 2. install diagnostic tools
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

    # step 3. create and build apps
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


def run_test(conf_file_path: str) -> None|Exception:
    pass


def post_run(conf_file_path: str) -> None|Exception:
    pass