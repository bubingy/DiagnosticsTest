import os

import instances.constants as constants
from services.config.DiagnosticToolsTest import load_diagtooltestconf
from instances.config import DiagnosticToolsTest as diag_tools_test_conf
from instances.logger import ScriptLogger
from services.project import consoleapp as consoleapp_service
from services.project import gcdumpapp as gcdumpapp_service
from services.project import webapp as webapp_service
from services.dotnet import sdk as sdk_service
from services.dotnet import cleaner as cleaner_service
from services.dotnet import tools as tools_service
from tasks.DiagnosticToolsTest import dotnet_counters
from tasks.DiagnosticToolsTest import dotnet_dump
from tasks.DiagnosticToolsTest import dotnet_gcdump
from tasks.DiagnosticToolsTest import dotnet_sos
from tasks.DiagnosticToolsTest import dotnet_stack
from tasks.DiagnosticToolsTest import dotnet_trace


def prepare_test_bed():
    '''Create folders for TestBed and TestResult.
    '''
    try:
        test_bed = os.path.join(
            diag_tools_test_conf.testbed_root,
            f'TestBed-{diag_tools_test_conf.test_name}'
        )
        if not os.path.exists(test_bed): os.makedirs(test_bed)

        test_result_root = os.path.join(
            test_bed,
            f'TestResult-{diag_tools_test_conf.test_name}'
        )
        if not os.path.exists(test_result_root): os.makedirs(test_result_root)
    except Exception as e:
        print(f'fail to create folders for TestBed and TestResult: {e}')
        exit(-1)


def run_test():
    load_diagtooltestconf(
        os.path.join(
            constants.configuration_root,
            'DiagnosticToolsTest.conf'
        )
    )

    prepare_test_bed()

    dotnet_logger = ScriptLogger(
        'dotnet',
        os.path.join(diag_tools_test_conf.test_result_root, 'dotnet.log')
    )
    sdk_service.install_sdk_from_script(
        diag_tools_test_conf.sdk_version,
        diag_tools_test_conf.testbed,
        diag_tools_test_conf.env['DOTNET_ROOT'],
        diag_tools_test_conf.rid,
        None,
        dotnet_logger
    )
    tools_service.install_diagnostic_tools(
        diag_tools_test_conf.dotnet_bin_path,
        diag_tools_test_conf.tool_root,
        diag_tools_test_conf.tool_version,
        diag_tools_test_conf.tool_feed,
        diag_tools_test_conf.env,
        dotnet_logger,
    )

    logger = ScriptLogger(
        'projects',
        os.path.join(diag_tools_test_conf.test_result_root,'projects.log')
    )
    consoleapp_service.create_build_consoleapp(
        diag_tools_test_conf.testbed,
        diag_tools_test_conf.dotnet_bin_path,
        diag_tools_test_conf.sdk_version,
        diag_tools_test_conf.env,
        logger
    )
    gcdumpapp_service.create_build_GCDumpPlayground(
        diag_tools_test_conf.testbed,
        diag_tools_test_conf.dotnet_bin_path,
        diag_tools_test_conf.sdk_version,
        diag_tools_test_conf.env,
        logger
    )
    webapp_service.create_build_webapp(
        diag_tools_test_conf.testbed,
        diag_tools_test_conf.dotnet_bin_path,
        diag_tools_test_conf.sdk_version,
        diag_tools_test_conf.env,
        logger
    )

    logger = ScriptLogger(
        'dotnet_counters',
        os.path.join(diag_tools_test_conf.test_result_root,'dotnet_counters.log')
    )
    dotnet_counters.test_dotnet_counters(logger)
    
    logger = ScriptLogger(
        'dotnet_dump',
        os.path.join(diag_tools_test_conf.test_result_root,'dotnet_dump.log')
    )
    dotnet_dump.test_dotnet_dump(logger)
    
    logger = ScriptLogger(
        'dotnet_gcdump',
        os.path.join(diag_tools_test_conf.test_result_root,'dotnet_gcdump.log')
    )
    dotnet_gcdump.test_dotnet_gcdump(logger)

    logger = ScriptLogger(
        'dotnet_sos',
        os.path.join(diag_tools_test_conf.test_result_root,'dotnet_sos.log')
    )
    dotnet_sos.test_dotnet_sos(logger)

    logger = ScriptLogger(
        'dotnet_stack',
        os.path.join(diag_tools_test_conf.test_result_root,'dotnet_stack.log')
    )
    dotnet_stack.test_dotnet_stack(logger)

    logger = ScriptLogger(
        'dotnet_trace',
        os.path.join(diag_tools_test_conf.test_result_root,'dotnet_trace.log')
    )
    dotnet_trace.test_dotnet_trace(logger)

    cleaner_service.remove_test_temp_directory(diag_tools_test_conf.rid, dotnet_logger)
    