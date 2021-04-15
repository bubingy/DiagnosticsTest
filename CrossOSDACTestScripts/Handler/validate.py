'''Analyze dumpfiles
'''

# coding=utf-8

import os

from config import configuration
from utils import run_command_async, PIPE


COMMANDS = [
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


def validate(dump_path: os.PathLike, output_path: os.PathLike):
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
        for command in COMMANDS:
            try:
                process.stdin.write(command)
            except Exception as exception:
                stream.write(f'{exception}\n'.encode('utf-8'))
                continue
        process.communicate()


def validate_32bit(dump_path: os.PathLike, output_path: os.PathLike):
    """ analyze dump file and redirect output to a file

    params
        dump_path: the path of dump file
        output_path: the path of output file
    """
    home_directory = os.getenv('HOME')

    with open(output_path, 'w+') as stream:
        tool_version = configuration.tool_version
        process = run_command_async(
            f'dotnet {home_directory}\\.dotnet\\tools\\.store\\' + \
            f'dotnet-dump\\{tool_version}\\dotnet-dump\\{tool_version}\\' + \
            f'tools\\netcoreapp2.1\\any\\dotnet-dump.dll analyze {dump_path}',
            stdin=PIPE,
            stdout=stream,
            stderr=stream
        )
        for command in COMMANDS:
            try:
                process.stdin.write(command)
            except Exception as exception:
                stream.write(f'{exception}\n'.encode('utf-8'))
                continue
        process.communicate()
