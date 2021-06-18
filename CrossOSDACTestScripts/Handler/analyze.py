'''Analyze dumpfiles
'''

# coding=utf-8

import os

from config import TestConfig
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


def analyze(conf: TestConfig, dump_path: os.PathLike):
    """ analyze dump file and redirect output to a file

    params
        dump_path: the path of dump file
    """
    dump_name = os.path.basename(dump_path)

    analyze_output_path = os.path.join(
        conf.analyze_output,
        dump_name.replace('dump', 'out')
    )
    with open(analyze_output_path, 'w+') as stream:
        if conf.rid == 'linux-musl-arm64':
            tool_version = conf.tool_version
            process = run_command_async(
                (
                    'dotnet '
                    f'{conf.tool_root}/.store/dotnet-dump/{tool_version}/dotnet-dump/{tool_version}/tools/netcoreapp2.1/any/dotnet-dump.dll '
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
