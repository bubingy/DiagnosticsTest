import os
import argparse

import instances.constants as constants
from services.config.LTTngTest import load_lttngtestconf
from services.sysinfo import get_rid
from services.dotnet.cleaner import remove_test_temp_directory
from tasks.LTTngTest.main import run_test


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument(
        'action',
        choices=['clean', 'run']
    )
    args = parser.parse_args()
    
    load_lttngtestconf(
        os.path.join(
            constants.configuration_root,
            'LTTngTest.conf'
        )
    )

    if args.action == 'clean':
        remove_test_temp_directory(get_rid())
    if args.action == 'run':
        run_test()