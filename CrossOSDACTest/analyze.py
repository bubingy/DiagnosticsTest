'''Analyze dumpfiles
'''

# coding=utf-8

import os

from CrossOSDACTest.config import TestConfig
from utils.terminal import run_command_async, PIPE


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
            command = (
                f'{conf.dotnet} '
                f'{conf.tool_root}/.store/dotnet-dump/{tool_version}/dotnet-dump/{tool_version}/tools/netcoreapp3.1/any/dotnet-dump.dll '
                f'analyze {dump_path}'
            )
        else:
            dotnet_dump_path = os.path.join(conf.tool_root, 'dotnet-dump')
            command = f'{dotnet_dump_path} analyze {dump_path}'

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
