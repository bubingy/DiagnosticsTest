import os
import glob

import instances.constants as constants
import instances.config.CrossOSDACTest as crossosdac_test_conf
import instances.project.oom as oom_conf
import instances.project.uhe as uhe_conf
from instances.logger import ScriptLogger
from services.terminal import run_command_async, PIPE
from services.dotnet import sdk as sdk_service
from services.dotnet import cleaner as cleaner_service
from services.dotnet import tools as tools_service
from services.config.CrossOSDACTest import load_crossosdactestconf


RAW_COMMANDS = [
    b'clrstack\n',
    b'clrstack -i\n',
    b'clrthreads\n',
    b'clrmodules\n',
    b'eeheap\n',
    b'dumpheap\n',
    b'printexception\n',
    b'dso\n',
    b'eeversion\n',
    b'exit\n'
]


def filter_32bit_dump(dump_directory: os.PathLike) -> list:
    return list(
        filter(
            lambda dump_name: 'linux-arm' in dump_name and '64' not in dump_name,
            os.listdir(dump_directory)
        )
    )


def filter_64bit_dump(dump_directory: os.PathLike) -> list:
    return list(
        filter(
            lambda dump_name: 'x64' in dump_name or 'arm64' in dump_name ,
            os.listdir(dump_directory)
        )
    )


def validate():
    load_crossosdactestconf(
        os.path.join(
            constants.configuration_root,
            'CrossOSDACTest.conf'
        )
    )

    for sdk_version in crossosdac_test_conf.sdk_version_list:
        logger = ScriptLogger(
            'CrossOSDAC-Validate',
            os.path.join(crossosdac_test_conf.validate_testbed, f'CrossOSDAC-Validate-net{sdk_version}.log')
        )

        dump_dir = os.path.join(
            crossosdac_test_conf.validate_testbed,
            f'dumpfiles-net{sdk_version}'
        )

        analyze_output_dir = os.path.join(
            crossosdac_test_conf.validate_testbed,
            f'analyzeoutput-net{sdk_version}'
        )

        for arch in ['x86', 'x64']:
            env = os.environ.copy()
            dotnet_root = os.path.join(
                crossosdac_test_conf.validate_testbed,
                f'dotnet-sdk-net{sdk_version}-windows-{arch}'
            )
            dotnet_bin_path = os.path.join(dotnet_root, 'dotnet.exe')
            tool_root = os.path.join(
                crossosdac_test_conf.validate_testbed,
                f'diag-tool-net{sdk_version}-ver{crossosdac_test_conf.tool_version}-windows-{arch}'
            )

            env['DOTNET_ROOT'] = dotnet_root
            env['PATH'] = f'{dotnet_root}:{tool_root}:' + env['PATH']

            sdk_service.install_sdk_from_script(
                sdk_version,
                crossosdac_test_conf.validate_testbed,
                dotnet_root,
                crossosdac_test_conf.rid,
                arch=arch,
                logger=logger
            )

            tools_service.install_tool(
                dotnet_bin_path,
                'dotnet-dump',
                tool_root,
                crossosdac_test_conf.tool_version,
                crossosdac_test_conf.tool_feed,
                env,
                logger
            )
            if arch == 'x86': 
                dump_name_list = filter_32bit_dump(dump_dir)
            if arch == 'x64': 
                dump_name_list = filter_64bit_dump(dump_dir)
            
            dotnet_dump_dll_path_pattern = os.path.join(
                f'{tool_root}', '.store', 'dotnet-dump', f'{crossosdac_test_conf.tool_version}',
                'dotnet-dump', f'{crossosdac_test_conf.tool_version}', 'tools', 'net*', 'any',
                'dotnet-dump.dll'
            )
            dotnet_dump_dll_path_candidates = glob.glob(dotnet_dump_dll_path_pattern)
            dotnet_dump_dll_path = dotnet_dump_dll_path_candidates[0]
            dotnet_dump_bin = f'{dotnet_bin_path} {dotnet_dump_dll_path}'

            for dump_name in dump_name_list:
                dump_path = os.path.join(dump_dir, dump_name)
                output_path = os.path.join(
                    analyze_output_dir,
                    dump_name.replace('dump', 'out') + '_win'
                )
                logger.info(f'start analyze {dump_path}')

                with open(output_path, 'w+') as stream:
                    process = run_command_async(
                        f'{dotnet_dump_bin} analyze {dump_path}',
                        stdin=PIPE,
                        stdout=stream,
                        stderr=stream
                    )
                    
                    if 'oom' in oom_conf.project_root:
                        project_bin_dir = os.path.join(oom_conf.project_root, 'out')
                    if 'uhe' in oom_conf.project_root:
                        project_bin_dir = os.path.join(uhe_conf.project_root, 'out')

                    COMMANDS = RAW_COMMANDS.copy()
                    COMMANDS.insert(0, f'setsymbolserver -directory {project_bin_dir}\n'.encode())
                    for command in COMMANDS:
                        try:
                            process.stdin.write(command)
                        except Exception as exception:
                            stream.write(f'{exception}\n'.encode('utf-8'))
                            continue
                    process.communicate()

            cleaner_service.remove_test_temp_directory(crossosdac_test_conf.rid, logger)
