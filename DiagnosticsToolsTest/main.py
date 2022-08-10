import os
import shutil

from DiagnosticsToolsTest import config
from infrastructure import sdk, tools
from utils.logger import ScriptLogger
from project import project_consoleapp, project_gcdumpapp, project_webapp
from DiagnosticsToolsTest import benchmark
from DiagnosticsToolsTest import dotnet_counters
from DiagnosticsToolsTest import dotnet_dump
from DiagnosticsToolsTest import dotnet_gcdump
from DiagnosticsToolsTest import dotnet_sos
from DiagnosticsToolsTest import dotnet_trace


def prepare_test_bed(configuration: config.TestConfig):
    '''Create folders for TestBed and TestResult.
    '''
    try:
        if not os.path.exists(configuration.test_bed):
            os.makedirs(configuration.test_bed)
        if not os.path.exists(configuration.test_result):
            os.makedirs(configuration.test_result)
    except Exception as e:
        print(f'fail to create folders for TestBed and TestResult: {e}')
        exit(-1)


def run_test(configuration: config.TestConfig):
    prepare_test_bed(configuration)
    logger = ScriptLogger(
        'initialize',
        os.path.join(
            configuration.test_result,
            'init.log'
        )
    )
    sdk.install_sdk(
        configuration.sdk_version,
        configuration.sdk_build_id,
        configuration.test_bed,
        configuration.rid,
        configuration.authorization,
        logger
    )
    tools.install_diagnostics_tools(
        configuration.tool_root,
        configuration.tool_version,
        configuration.tool_feed,
        logger,
        configuration.dotnet
    )
    logger = ScriptLogger(
        'projects',
        os.path.join(
            configuration.test_result,
            'projects.log'
        )
    )
    project_consoleapp.create_build_consoleapp(configuration, logger)
    project_gcdumpapp.create_build_GCDumpPlayground(configuration, logger)
    project_webapp.create_build_webapp(configuration, logger)

    logger = ScriptLogger(
        'benchmark',
        os.path.join(
            configuration.test_result,
            'benchmark.log'
        )
    )
    benchmark.download_diagnostics(configuration, logger)
    benchmark.run_benchmark(configuration, logger)

    logger = ScriptLogger(
        'dotnet_counters',
        os.path.join(
            configuration.test_result,
            'dotnet_counters.log'
        )
    )
    dotnet_counters.test_dotnet_counters(configuration, logger)
    
    logger = ScriptLogger(
        'dotnet_dump',
        os.path.join(
            configuration.test_result,
            'dotnet_dump.log'
        )
    )
    dotnet_dump.test_dotnet_dump(configuration, logger)
    
    logger = ScriptLogger(
        'dotnet_gcdump',
        os.path.join(
            configuration.test_result,
            'dotnet_gcdump.log'
        )
    )
    dotnet_gcdump.test_dotnet_gcdump(configuration, logger)
    
    logger = ScriptLogger(
        'dotnet_sos',
        os.path.join(
            configuration.test_result,
            'dotnet_sos.log'
        )
    )
    dotnet_sos.test_dotnet_sos(configuration, logger)

    logger = ScriptLogger(
        'dotnet_trace',
        os.path.join(
            configuration.test_result,
            'dotnet_trace.log'
        )
    )
    dotnet_trace.test_dotnet_trace(configuration, logger)


def clean(configuration: config.TestConfig):

    if 'win' in configuration.rid: home_path = os.environ['USERPROFILE']
    else: home_path = os.environ['HOME']

    to_be_removed = [
        os.path.join(home_path, '.aspnet'),
        os.path.join(home_path, '.dotnet'),
        os.path.join(home_path, '.nuget'),
        os.path.join(home_path, '.templateengine'),
        os.path.join(home_path, '.lldb'),
        os.path.join(home_path, '.lldbinit'),
        os.path.join(home_path, '.local'),
        configuration.test_bed
    ]

    print('Following files or dirs would be removed:')
    for f in to_be_removed: print(f'    {f}')
    key = input('input `y` to continue, other input will be take as a no:')
    if key != 'y': exit(0)

    for f in to_be_removed:
        if not os.path.exists(f): continue
        if os.path.isdir(f): shutil.rmtree(f)
        else: os.remove(f)
    