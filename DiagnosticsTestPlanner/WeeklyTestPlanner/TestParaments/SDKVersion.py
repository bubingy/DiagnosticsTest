# coding=utf-8

import os

from utils.conf import AzureQueryConf, WeeklyTestConf
from utils.azure import get_artifact_version, \
    get_latest_acceptable_build, get_artifact
from utils.github import list_branches


def get_latest_branches(major_version: str, branch_list: list):
    '''Get latest branch of given major version of .NET installer
    
    '''
    return max(
        map(
            lambda x: x['name'],
            filter(
                lambda x: f'release/{major_version}' in x['name'][:12],
                branch_list
            )
        )
    ) 


def get_sdk_version():
    '''Print out latest `release` version of .net core 3, .net 5 and .net 6.

    '''
    azure_conf = AzureQueryConf(
        os.path.join(
            os.environ['planner_conf_dir'],
            'azure.ini'
        )
    )

    test_conf = WeeklyTestConf(
        os.path.join(
            os.environ['planner_conf_dir'],
            'weekly_test.ini'
        )
    )

    sdk_version = dict()
    branch_list = list_branches('dotnet', 'installer')
    for major_version in test_conf.major_version_list:
        branch_name = get_latest_branches(major_version, branch_list)
        
        build = get_latest_acceptable_build(
            azure_conf.definition_id_map['installer'],
            azure_conf.authorization, 
            branch_name
        )
        artifact = get_artifact(build, azure_conf.authorization)
        version = get_artifact_version(artifact, azure_conf.authorization)
        sdk_version[major_version] = version
    return sdk_version
