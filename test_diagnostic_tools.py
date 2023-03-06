import os
import argparse

import instances.constants as constants
from services.sysinfo import get_rid
from services.container import run_in_container
from services.dotnet.cleaner import remove_test_temp_directory
from services.config.DiagnosticToolsTest import load_diagtooltestconf
from tasks.DiagnosticToolsTest.main import run_test


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument(
        'action',
        choices=['clean', 'deploy', 'run']
    )
    args = parser.parse_args()

    load_diagtooltestconf(
        os.path.join(
            constants.configuration_root,
            'DiagnosticToolsTest.conf'
        )
    )

    if args.action == 'clean':
        remove_test_temp_directory(get_rid())
    if args.action == 'deploy':
        run_in_container()
    if args.action == 'run':
        run_test()
