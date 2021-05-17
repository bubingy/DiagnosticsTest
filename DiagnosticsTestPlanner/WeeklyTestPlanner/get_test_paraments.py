# coding=utf-8

import argparse
from datetime import datetime

import OSRotation.get_os_rotation as osr
import TestParaments.SDKVersion as sdk
from TestParaments.ToolInfo import ToolInfo
from utils import print_test_result_page


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--output')
    args = parser.parse_args()
    output_file = args.output
    os_rotation = osr.get_os_rotation(
        datetime.today().strftime('%Y-%m-%d')
    )
    sdk_version = sdk.get_sdk_version()
    tool_info = ToolInfo()
    print_test_result_page(os_rotation, sdk_version, tool_info, output_file)