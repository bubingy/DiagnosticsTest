'''Run CrossOSDAC test.'''

# coding=utf-8

import argparse

from Handler import handler

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    linux_parser = parser.add_argument_group('analyze', 'analyze on linux')
    linux_parser.add_argument(
        '--analyze',
        action='store_true',
        default=False,
        help="analyze on linux."
    )
    windows_parser = parser.add_argument_group('validate', 'validate on windows')
    windows_parser.add_argument('-d', '--dump-path', help='the path of dump file')
    windows_parser.add_argument('-o', '--output-path', help='the path of output file')

    args = parser.parse_args()

    if args.analyze:
        handler.analyze_on_linux()
    else:
        dump_path = args.dump_path
        output_path = args.output_path
        handler.validate_on_windows(dump_path, output_path)
