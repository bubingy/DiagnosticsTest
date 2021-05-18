# coding=utf-8

import os
import argparse
from datetime import datetime

import WeeklyTestPlanner.OSRotation.get_os_rotation as osr
import WeeklyTestPlanner.TestParaments.SDKVersion as sdk
from WeeklyTestPlanner.TestParaments.ToolInfo import ToolInfo
from utils.print import print_weekly_test_plan, print_release_test_matrix
from utils.conf import TestConf


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--output')
    parser.add_argument('--type', choices=['weekly', 'release'])
    args = parser.parse_args()
    output_file = args.output
    test_type = args.type
    
    if test_type == 'weekly':
        os_rotation = osr.get_os_rotation(
            datetime.today().strftime('%Y-%m-%d')
        )
        sdk_version = sdk.get_sdk_version()
        tool_info = ToolInfo()
        print_weekly_test_plan(os_rotation, sdk_version, tool_info, output_file)

    if test_type == 'release':
        test_conf = TestConf(
            os.path.join(
                os.path.dirname(os.path.abspath(__file__)),
                'conf',
                'release_test.ini'
            )
        )
        print_release_test_matrix(test_conf, output_file)