import os
import argparse

import app
from LTTng import test_runner
from LTTng import configuration


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-c', '--configuration',
        help='run the test',
        dest='configuration_path',
        default=os.path.join(app.script_root, 'TestConfiguration', 'LTTng.conf') 
    )
    args = parser.parse_args()

    configuration_path = args.configuration_path
    test_conf = configuration.LTTngTestConfiguration(configuration_path)

    test_runner.init_test(test_conf)
    for run_conf in test_conf.run_conf_list:
        test_runner.install_DotNET_SDK(run_conf)
        test_runner.prepare_sample_app(run_conf)
        test_runner.run_test_for_single_SDK(run_conf)
        test_runner.clean_temp(run_conf)