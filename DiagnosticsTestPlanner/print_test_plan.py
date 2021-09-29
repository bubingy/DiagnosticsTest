# coding=utf-8

import os
import argparse
from datetime import datetime

from WeeklyTestPlanner.OSRotation.get_os_rotation import get_os_rotation
from WeeklyTestPlanner.TestParaments.SDKVersion import get_sdk_version
from WeeklyTestPlanner.TestParaments.ToolInfo import get_tool_info
from utils.print import print_weekly_test_plan, print_release_test_matrix
from utils.conf import ReleaseTestConf


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--output')
    parser.add_argument('--type', choices=['weekly', 'release'])
    args = parser.parse_args()
    output_file = args.output
    test_type = args.type
    
    if test_type == 'weekly':
        os_rotation = get_os_rotation(
            datetime.today().strftime('%Y-%m-%d')
        )
        sdk_version = get_sdk_version()
        tool_version, pr_info, tool_feed = get_tool_info()
        print_weekly_test_plan(os_rotation, sdk_version, tool_version, pr_info, output_file)

    if test_type == 'release':
        test_conf = ReleaseTestConf(
            os.path.join(
                os.path.dirname(os.path.abspath(__file__)),
                'conf',
                'release_test.ini'
            )
        )
        print_release_test_matrix(test_conf, output_file)