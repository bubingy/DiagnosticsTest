'''Analyze dumpfiles
'''

# coding=utf-8

import os
import glob

from utils.terminal import run_command_async, PIPE
from CrossOSDACTest.config import TestConfig


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


def validate(conf: TestConfig, dump_path: os.PathLike, output_path: os.PathLike):
    """ analyze dump file and redirect output to a file

    params
        dump_path: the path of dump file
        output_path: the path of analyze output
    """
    with open(output_path, 'w+') as stream:
        process = run_command_async(
            f'dotnet-dump analyze {dump_path}',
            stdin=PIPE,
            stdout=stream,
            stderr=stream
        )
        project_name = os.path.basename(dump_path)[5:]
        project_bin_dir = os.path.join(conf.test_bed, project_name, 'out')
        COMMANDS = RAW_COMMANDS.copy()
        COMMANDS.insert(0, f'setsymbolserver -directory {project_bin_dir}\n'.encode())
        for command in COMMANDS:
            try:
                process.stdin.write(command)
            except Exception as exception:
                stream.write(f'{exception}\n'.encode('utf-8'))
                continue
        process.communicate()


def validate_32bit(conf: TestConfig, dump_path: os.PathLike, output_path: os.PathLike):
    """ analyze dump file and redirect output to a file

    params
        dump_path: the path of dump file
        output_path: the path of output file
    """
    with open(output_path, 'w+') as stream:
        tool_version = conf.tool_version
        dotnet_dump_dll_path_pattern = os.path.join(
            f'{conf.tool_root}', '.store', 'dotnet-dump', f'{tool_version}',
            'dotnet-dump', f'{tool_version}', 'tools', 'net*', 'any',
            'dotnet-dump.dll'
        )
        dotnet_dump_dll_path_candidates = glob.glob(dotnet_dump_dll_path_pattern)
        dotnet_dump_dll_path = dotnet_dump_dll_path_candidates[0]
        process = run_command_async(
            (
                f'{conf.dotnet} '
                f'{dotnet_dump_dll_path} '
                f'analyze {dump_path}'
            ),
            stdin=PIPE,
            stdout=stream,
            stderr=stream
        )
        project_name = os.path.basename(dump_path)[5:]
        project_bin_dir = os.path.join(conf.test_bed, project_name, 'out')
        COMMANDS = RAW_COMMANDS.copy()
        COMMANDS.insert(0, f'setsymbolserver -directory {project_bin_dir}\n'.encode())
        for command in COMMANDS:
            try:
                process.stdin.write(command)
            except Exception as exception:
                stream.write(f'{exception}\n'.encode('utf-8'))
                continue
        process.communicate()
