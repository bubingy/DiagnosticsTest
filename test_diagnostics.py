import argparse

from DiagnosticsToolsTest import main, config


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('action',
                    choices=['run', 'clean'],
                    help='specify the action')
    args = parser.parse_args()

    configuration = config.TestConfig()
    if args.action == 'run': main.run_test(configuration)
    if args.action == 'clean': main.clean(configuration)