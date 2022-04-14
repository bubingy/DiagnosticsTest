import os
import argparse

from LTTngTest import main, config


if __name__ == '__main__':
    if os.geteuid() != 0:
        print('You need root permissions.')
        exit()
    parser = argparse.ArgumentParser()
    parser.add_argument('action',
                    choices=['run', 'clean'],
                    help='specify the action')
    args = parser.parse_args()

    global_conf = config.GlobalConfig()
    if args.action == 'run': main.run_test(global_conf)
    if args.action == 'clean': main.clean(global_conf)
