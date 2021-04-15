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
    b'printexception\n'
    b'dso\n',
    b'eeversion\n',
    b'exit\n'
]


def analyze(dump_path, output_path=None):
    """ analyze dump file and redirect output to a file

    params
        dump_path: the path of dump file
    """
    project_name = dump_path.split('_')[-1]

    if output_path is not None:
        analyze_output_path = output_path
    else:
        analyze_output_path = os.path.join(
            configuration.analyze_output,
            '_'.join(
                [
                    'out',
                    f'net{configuration.sdk_version[0]}{configuration.sdk_version[2]}',
                    configuration.rid,
                    project_name
                ]
            )
        )
    with open(analyze_output_path, 'w+') as stream:
        if configuration.rid == 'linux-musl-arm64':
            home_path = os.environ['HOME']
            tool_version = configuration.tool_version
            process = run_command_async(
                (
                    'dotnet '
                    f'{home_path}/.dotnet/tools/.store/dotnet-dump/{tool_version}/dotnet-dump/{tool_version}/tools/netcoreapp2.1/any/dotnet-dump.dll '
                    f'analyze {dump_path}'
                ),
                stdin=PIPE,
                stdout=stream,
                stderr=stream
            )
        else:
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
