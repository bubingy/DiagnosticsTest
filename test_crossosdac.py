import os
import argparse

import instances.constants as constants
from services.config.CrossOSDACTest import load_crossosdactestconf
from services.sysinfo import get_rid
from services.dotnet.cleaner import remove_test_temp_directory
from tasks.CrossOSDACTest.analyze import analyze
from tasks.CrossOSDACTest.validate import validate


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument(
        'action',
        choices=['clean', 'analyze', 'validate']
    )
    parser.add_argument('--deploy', action='store_true')
    args = parser.parse_args()

    load_crossosdactestconf(
        os.path.join(
            constants.configuration_root,
            'CrossOSDACTest.conf'
        )
    )

    if args.action == 'clean':
        remove_test_temp_directory(get_rid())
    if args.action == 'analyze':
        analyze()
    if args.action == 'validate':
        validate()
