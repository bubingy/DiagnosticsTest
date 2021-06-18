'''Run CrossOSDAC test.'''

# coding=utf-8

import argparse

from Handler import handler
from config import GlobalConfig

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        'action',
        choices=['analyze', 'validate'],
        help='decide which task this script to do.'
    )
    analyze_parser = parser.add_argument_group(
        'analyze',
        'analyze on Linux'
    )

    validate_parser = parser.add_argument_group(
        'validate',
        'validate on Windows'
    )
    args = parser.parse_args()

    global_conf = GlobalConfig()

    if args.action == 'analyze':
        handler.analyze_on_linux(global_conf)
    elif args.action == 'validate':
        handler.validate_on_windows()
    else:
        raise f'unknown action: {args.action}'
