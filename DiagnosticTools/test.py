import os

import app
from app import AppLogger
from DiagnosticTools.configuration import DiagToolsTestConfiguration, parse_conf_file
from tools import sdk_runtime, dotnet_tool

def pre_run(test_conf: DiagToolsTestConfiguration) -> dict|Exception:
    """Initialization of test
    
    :param test_conf: DiagToolsTestConfiguration instance
    """
    # step 0. create testbed and test result folder 
    os.makedirs(test_conf.testbed, exist_ok=True)
    os.makedirs(test_conf.test_result_folder, exist_ok=True)
    # step 1. install .NET SDK
    log_file_path = os.path.join(test_conf.test_result_folder, 'sdk_install.log')
    app.logger = AppLogger('.NET Installation', log_file_path)

    script_path = os.path.join(test_conf.testbed, 'dotnet_install')
    script_path = sdk_runtime.donwload_install_script(test_conf.rid, script_path)
    script_path = sdk_runtime.enable_runnable(test_conf.rid, script_path)

    dotnet_root = sdk_runtime.install_sdk_from_script(
        test_conf.rid, script_path, test_conf.dotnet_sdk_version, test_conf.dotnet_root)
    
    if isinstance(dotnet_root, Exception): 
        return dotnet_root
    
    # step 2. install diagnostic tools
    log_file_path = os.path.join(test_conf.test_result_folder, 'tool_install.log')
    app.logger = AppLogger('Tools Installation', log_file_path)

    tool_install_result = dict()
    for tool_name in test_conf.diag_tool_to_install:
        try:
            tool_root = dotnet_tool.install_tool(
                test_conf.dotnet_bin_path,
                tool_name,
                test_conf.diag_tool_root,
                test_conf.diag_tool_version,
                test_conf.diag_tool_feed,
                test_conf.env)

            if isinstance(tool_root, Exception):
                tool_install_result[tool_name] = False
            else:
                tool_install_result[tool_name] = True
        except:
            tool_install_result[tool_name] = False
            continue

    # step 3. create and build apps

    


def run_test(conf_file_path: str) -> None|Exception:
    try:
        test_conf = parse_conf_file(conf_file_path)
        os.makedirs(test_conf.testbed, exist_ok=True)
    except Exception as ex:
        test_conf = Exception(f'fail to initialize test environment: {ex}')