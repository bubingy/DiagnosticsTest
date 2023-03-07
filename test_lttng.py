import os
import argparse

import instances.constants as constants
import instances.config.LTTngTest as lttng_test_conf
from services.config.LTTngTest import load_lttngtestconf
from services.sysinfo import get_rid
from services.container import run_in_container
from services.dotnet.cleaner import remove_test_temp_directory
from tasks.LTTngTest.main import run_test


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument(
        'action',
        choices=['clean', 'deploy', 'run']
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
    if args.action == 'deploy':
        run_in_container(
            lttng_test_conf.docker_base_url,
            lttng_test_conf.dockerfile_url,
            lttng_test_conf.full_tag,
            lttng_test_conf.mount_dir,
            lttng_test_conf.test_name,
            lttng_test_conf.cap_add,
            lttng_test_conf.security_opt,
            'python3 test_lttng.py run'
        )
    if args.action == 'run':
        run_test()