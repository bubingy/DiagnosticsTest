import os
import argparse

import instances.constants as constants
import instances.config.CrossOSDACTest as crossosdac_test_conf
from services.config.CrossOSDACTest import load_crossosdactestconf
from services.sysinfo import get_rid
from services.container import run_in_container
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
        if args.deploy is True:
            run_in_container(
                crossosdac_test_conf.docker_base_url,
                crossosdac_test_conf.dockerfile_url,
                crossosdac_test_conf.full_tag,
                crossosdac_test_conf.mount_dir,
                crossosdac_test_conf.test_name,
                crossosdac_test_conf.cap_add,
                crossosdac_test_conf.security_opt,
                crossosdac_test_conf.privileged,
                'python3 test_crossosdac.py analyze'
            )
        else:
            analyze()
    if args.action == 'validate':
        validate()
