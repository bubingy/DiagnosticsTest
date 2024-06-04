import os
import argparse

import app
from DiagnosticTools import test_runner
from DiagnosticTools import configuration

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-a', '--action',
        help='specify',
        dest='action',
        choices=['run', 'clean', 'restore']
    )
    parser.add_argument(
        '-c', '--configuration',
        help='run the test',
        dest='configuration_path',
        default=os.path.join(app.script_root, 'TestConfiguration', 'DiagToolsTest.conf') 
    )
    args = parser.parse_args()

    if args.action == 'run':
        configuration_path = args.configuration_path
        test_conf = configuration.DiagToolsTestConfiguration(configuration_path)
        test_runner.init_test(test_conf)
        test_runner.install_DotNET_SDK(test_conf)
        test_runner.install_diagnostic_tools(test_conf)
        test_runner.prepare_sample_app(test_conf)
        test_runner.run_test(test_conf)

    if args.action == 'clean':
        configuration_path = args.configuration_path
        test_conf = configuration.DiagToolsTestConfiguration(configuration_path)
        test_runner.clean_temp(test_conf)

    if args.action == 'restore':
        configuration_path = args.configuration_path
        test_conf = configuration.DiagToolsTestConfiguration(configuration_path)
        test_runner.restore_temp(test_conf)

