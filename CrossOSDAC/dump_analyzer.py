import os
import glob
from subprocess import PIPE

import app
from tools import dotnet_tool
from tools import dotnet_app
from tools import terminal
from CrossOSDAC.configuration import RunConfiguration


basic_analyze_commands = [
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


def __filter_32bit_dump(dump_path_list: list[str]) -> list[str]:
    return list(
        filter(
            lambda dump_name: 'linux-arm' in dump_name and 'linux-arm64' not in dump_name,
            dump_path_list
        )
    )


def __filter_64bit_dump(dump_path_list: list[str]) -> list[str]:
    return list(
        filter(
            lambda dump_name: 'x64' in dump_name or 'arm64' in dump_name ,
            dump_path_list
        )
    )


@app.function_monitor(
    pre_run_msg='------ start to analyze dump ------',
    post_run_msg='------ analyze dump completed ------'
)
def analyze_dump(test_conf: RunConfiguration):
    '''Run sample apps and perform tests.

    '''
    tool_dll_path = dotnet_tool.get_tool_dll(
        'dotnet-dump',
        test_conf.diag_tool_version,
        test_conf.diag_tool_root
    )
    if isinstance(tool_dll_path, Exception):
        return tool_dll_path
    
    # analyze dump with dotnet-dump analyze
    dump_path_template = os.path.join(test_conf.dump_folder, 'dump_*')
    dump_path_candidates = glob.glob(dump_path_template)
    if len(dump_path_candidates) < 1:
        return Exception('no dump file is generated')
    
    # linux case
    if test_conf.arch is None:
        dump_path_list = dump_path_candidates
    # windows case
    else:
        if test_conf.arch == 'x86':
            dump_path_list = __filter_32bit_dump(dump_path_candidates)
        else:
            dump_path_list = __filter_64bit_dump(dump_path_candidates)

    for dump_path in dump_path_list:
        dump_name = os.path.basename(dump_path)
        analyze_output_path = os.path.join(
            test_conf.analyze_folder,
            dump_name.replace('dump', 'analyze')
        )

        analyze_commands = basic_analyze_commands.copy()
        
        # analyze dump on windows
        if test_conf.arch is not None:
            analyze_output_path = f'{analyze_output_path}_win'

            app_name = dump_name.replace('dump_', '')
            app_root = os.path.join(test_conf.test_bed, app_name)
            project_bin_path = dotnet_app.get_app_bin(app_name, app_root)
            project_bin_dir = os.path.dirname(project_bin_path)
            analyze_commands.insert(
                0,
                f'setsymbolserver -directory {project_bin_dir}\n'.encode()
            )
            
        async_args = [test_conf.dotnet_bin_path, tool_dll_path, 'analyze', dump_path]
        
        with open(analyze_output_path, 'wb+') as fp:
            _, proc = terminal.run_command_async(async_args, stdin=PIPE, stdout=fp, stderr=fp, env=test_conf.env)

            for command in analyze_commands:
                try:
                    proc.stdin.write(command)
                except Exception as exception:
                    fp.write(f'{exception}\n'.encode('utf-8'))
                    continue
            proc.communicate()


