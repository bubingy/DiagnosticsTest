import os
import argparse

from CrossOSDACTest import main, config


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('action',
                    choices=['analyze', 'validate'],
                    help='specify the action')
    args = parser.parse_args()

    global_conf = config.GlobalConfig()
    if args.action == 'analyze': main.run_test(global_conf, 'analyze')
    if args.action == 'validate': main.run_test(global_conf, 'validate')
