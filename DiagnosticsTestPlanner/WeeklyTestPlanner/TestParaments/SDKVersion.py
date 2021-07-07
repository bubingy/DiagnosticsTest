# coding=utf-8

import os
from urllib import request

from utils.conf import WeeklyTestConf
# from utils.github import list_branches


# def get_latest_branches(major_version: str, branch_list: list):
#     '''Get latest branch of given major version of .NET installer
    
#     '''
#     return max(
#         map(
#             lambda x: x['name'],
#             filter(
#                 lambda x: f'release/{major_version}' in x['name'][:12],
#                 branch_list
#             )
#         )
#     ) 


def get_sdk_version():
    '''Print out latest `release` version of .net core 3, .net 5 and .net 6.

    '''
    test_conf = WeeklyTestConf(
        os.path.join(
            os.environ['planner_conf_dir'],
            'weekly_test.ini'
        )
    )

    sdk_version = dict()
    # branch_list = list_branches('dotnet', 'installer')
    for major_version, branch_name in zip(
        test_conf.major_version_list, test_conf.branch_list):
        # branch_name = get_latest_branches(major_version, branch_list)
        if major_version == '6.0':
            url = (
                'https://dotnetcli.blob.core.windows.net/'
                f'dotnet/Sdk/main/latest.version'
            )
        else:
            url = (
                'https://dotnetcli.blob.core.windows.net/'
                f'dotnet/Sdk/release/{branch_name}/latest.version'
            )
        response = request.urlopen(url)
        lines = response.readlines()
        for line in lines:
            content = line.decode('utf-8')
            if '-' in content or '.' in content:
                sdk_version[major_version] = content.strip('\r\n')
    return sdk_version
