import os
import argparse

import instances.constants as constants
import instances.config.DiagnosticToolsTest as diag_tools_test_conf
from services.config.DiagnosticToolsTest import load_diagtooltestconf
from services.sysinfo import get_rid
from services.container import run_in_container
from services.dotnet.cleaner import remove_test_temp_directory
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
        run_in_container(
            diag_tools_test_conf.docker_base_url,
            diag_tools_test_conf.dockerfile_url,
            diag_tools_test_conf.full_tag,
            diag_tools_test_conf.mount_dir,
            diag_tools_test_conf.test_name,
            diag_tools_test_conf.cap_add,
            diag_tools_test_conf.security_opt,
            'python3 test_diagnostic_tools.py run'
        )
    if args.action == 'run':
        run_test()
