# coding=utf-8

import os
from urllib import request

from utils.conf import WeeklyTestConf


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
    for branch_name in test_conf.branch_list:
        if '6.0' in branch_name:
            url = (
                'https://dotnetcli.blob.core.windows.net/'
                f'dotnet/Sdk/main/latest.version'
            )
        else:
            url = (
                'https://dotnetcli.blob.core.windows.net/'
                f'dotnet/Sdk/{branch_name.lower()}/latest.version'
            )
        response = request.urlopen(url)
        lines = response.readlines()
        for line in lines:
            content = line.decode('utf-8')
            if '-' in content or '.' in content:
                sdk_version[branch_name] = content.strip('\r\n')

    return sdk_version
