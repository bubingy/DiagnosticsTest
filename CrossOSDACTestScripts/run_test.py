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
    args = parser.parse_args()

    if args.action == 'analyze':
        handler.analyze_on_linux()
    elif args.action == 'init':
        arch = args.architecture
        handler.init_on_windows(arch)
    else:
        handler.validate_on_windows()
