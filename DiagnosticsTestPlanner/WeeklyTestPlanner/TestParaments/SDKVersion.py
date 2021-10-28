# coding=utf-8

import os

from utils.conf import WeeklyTestConf, AzureQueryConf
from utils.azure import get_latest_acceptable_build, \
    get_artifact, get_artifact_version


def get_sdk_version():
    '''Print out latest `release` version of .net core 3, .net 5 and .net 6.

    '''
    test_conf = WeeklyTestConf(
        os.path.join(
            os.environ['planner_conf_dir'],
            'weekly_test.ini'
        )
    )

    azure_conf = AzureQueryConf(
        os.path.join(
            os.environ['planner_conf_dir'],
            'azure.ini'
        )
    )

    sdk_version = dict()

    for branch_name in test_conf.branch_list:
        build_info = get_latest_acceptable_build(
            azure_conf.definition_id_map['installer'],
            azure_conf.authorization,
            branch_name.lower()
        )
        artifact_info = get_artifact(
            build_info,
            azure_conf.authorization
        ) 
        artifact_version = get_artifact_version(
            artifact_info,
            azure_conf.authorization
        )
        sdk_version[branch_name] = artifact_version
    # for branch_name in test_conf.branch_list:
    #     if '3.1' in branch_name:
    #         url = (
    #             'https://dotnetcli.blob.core.windows.net/'
    #             f'dotnet/Sdk/{branch_name.lower()}/latest.version'
    #         )
    #     else:
    #         url = (
    #             f'https://aka.ms/dotnet/{branch_name.lower()}'
    #             '/daily/Sdk/productCommit-win-x64.txt'
    #         )
    #     response = request.urlopen(url)
    #     lines = response.readlines()
    #     for line in lines:
    #         content = line.decode('utf-8')
    #         if '-' in content or '.' in content:
    #             sdk_version[branch_name] = content.strip('\r\n')

    return sdk_version
