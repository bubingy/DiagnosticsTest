import os

import instances.constants as constants
import instances.config.CrossOSDACTest as crossosdac_test_conf
from instances.logger import ScriptLogger
from services.terminal import run_command_async, PIPE
from services.project import oom as oom_service
from services.project import uhe as uhe_service
from services.dotnet import sdk as sdk_service
from services.dotnet import cleaner as cleaner_service
from services.dotnet import tools as tools_service
from services.config.CrossOSDACTest import load_crossosdactestconf


COMMANDS = [
    b'clrstack\n',
    b'clrstack -i\n',
    b'clrthreads\n',
    b'clrmodules\n',
    b'eeheap\n',
    b'dumpheap\n',
    b'printexception\n'
    b'dso\n',
    b'eeversion\n',
    b'exit\n'
]


def prepare_analyze_test_bed():
    '''Create folders for TestBed.
    '''
    try:
        if not os.path.exists(crossosdac_test_conf.analyze_testbed):
            os.makedirs(crossosdac_test_conf.analyze_testbed)
    except Exception as e:
        print(f'fail to create folders: {e}')
        exit(-1)


def analyze():
    load_crossosdactestconf(
        os.path.join(
            constants.configuration_root,
            'CrossOSDACTest.conf'
        )
    )
    prepare_analyze_test_bed()

    for sdk_version in crossosdac_test_conf.sdk_version_list:
        logger = ScriptLogger(
            'CrossOSDAC-Analyze',
            os.path.join(crossosdac_test_conf.analyze_testbed, f'CrossOSDAC-Analyze-net{sdk_version}.log')
        )

        env = os.environ.copy()
        dotnet_root = os.path.join(
            crossosdac_test_conf.analyze_testbed,
            f'dotnet-sdk-net{sdk_version}-{crossosdac_test_conf.rid}'
        )
        tool_root = os.path.join(
            crossosdac_test_conf.analyze_testbed,
            f'diag-tool-net{sdk_version}-ver{crossosdac_test_conf.tool_version}-{crossosdac_test_conf.rid}'
        )

        env['DOTNET_ROOT'] = dotnet_root
        env['PATH'] = f'{dotnet_root}:{tool_root}:' + env['PATH']
        
        sdk_service.install_sdk_from_script(
            sdk_version,
            crossosdac_test_conf.analyze_testbed,
            dotnet_root,
            crossosdac_test_conf.rid,
            arch=None,
            logger=logger
        )

        tools_service.install_tool(
            os.path.join(dotnet_root, 'dotnet'),
            'dotnet-dump',
            tool_root,
            crossosdac_test_conf.tool_version,
            crossosdac_test_conf.tool_feed,
            env,
            logger
        )

        dump_path_dir = os.path.join(
            crossosdac_test_conf.analyze_testbed,
            f'dumpfiles-net{sdk_version}'
        )

        analyze_output_dir = os.path.join(
            crossosdac_test_conf.analyze_testbed,
            f'analyzeoutput-net{sdk_version}'
        )

        dotnet_dump_path = os.path.join(tool_root, 'dotnet-dump')

        # create and run oom
        oom_service.create_build_oom(
            crossosdac_test_conf.analyze_testbed,
            os.path.join(dotnet_root, 'dotnet'),
            env,
            crossosdac_test_conf.rid,
            sdk_version,
            logger
        )
        dump_path = oom_service.run_oom(
            env,
            dump_path_dir,
            sdk_version,
            crossosdac_test_conf.rid,
            logger
        )
        command = f'{dotnet_dump_path} analyze {dump_path}'
        dump_name = os.path.basename(dump_path)
        analyze_output_path = os.path.join(
            analyze_output_dir,
            dump_name.replace('dump', 'out')
        )
        with open(analyze_output_path, 'w+') as stream:
            process = run_command_async(
                command,
                stdin=PIPE,
                stdout=stream,
                stderr=stream
            )
            for analyze_command in COMMANDS:
                try:
                    process.stdin.write(analyze_command)
                except Exception as exception:
                    stream.write(f'{exception}\n'.encode('utf-8'))
                    continue
            process.communicate()
            
        # create and run uhe
        uhe_service.create_build_uhe(
            crossosdac_test_conf.analyze_testbed,
            os.path.join(dotnet_root, 'dotnet'),
            env,
            crossosdac_test_conf.rid,
            sdk_version,
            logger
        )
        dump_path = uhe_service.run_uhe(
            env,
            dump_path_dir,
            sdk_version,
            crossosdac_test_conf.rid,
            logger
        )
        command = f'{dotnet_dump_path} analyze {dump_path}'
        dump_name = os.path.basename(dump_path)
        analyze_output_path = os.path.join(
            analyze_output_dir,
            dump_name.replace('dump', 'out')
        )
        with open(analyze_output_path, 'w+') as stream:
            process = run_command_async(
                command,
                stdin=PIPE,
                stdout=stream,
                stderr=stream
            )
            for analyze_command in COMMANDS:
                try:
                    process.stdin.write(analyze_command)
                except Exception as exception:
                    stream.write(f'{exception}\n'.encode('utf-8'))
                    continue
            process.communicate()

        cleaner_service.remove_test_temp_directory(crossosdac_test_conf.rid, logger)   
