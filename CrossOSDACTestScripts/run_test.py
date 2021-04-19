'''Run CrossOSDAC test.'''

# coding=utf-8

import sys
import argparse

from Handler import handler

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        'action',
        choices=['analyze', 'validate', 'init'],
        help='decide which task this script to do.'
    )
    analyze_parser = parser.add_argument_group(
        'analyze',
        'analyze on Linux'
    )
    init_win_parser = parser.add_argument_group(
        'init',
        'install sdk and tool on Windows'
    )
    init_win_parser.add_argument(
        '-a', '--architecture',
        required=('init' in sys.argv),
        choices=['x86', 'x64'],
        help='specify the bit width of CPU.'
    )
    validate_parser = parser.add_argument_group(
        'validate',
        'validate on Windows'
    )
    validate_parser.add_argument(
        '-d', '--dump',
        required=('validate' in sys.argv),
        help='the path of dump file or directory contains dump files'
    )
    validate_parser.add_argument(
        '-o', '--output',
        required=('validate' in sys.argv),
        help='the path of output file  or directory contains output files'
    )
    args = parser.parse_args()

    if args.action == 'analyze':
        handler.analyze_on_linux()
    elif args.action == 'init':
        arch = args.architecture
        handler.init_on_windows(arch)
    else:
        dump_path = args.dump
        output_path = args.output
        handler.validate_on_windows(dump_path, output_path)
