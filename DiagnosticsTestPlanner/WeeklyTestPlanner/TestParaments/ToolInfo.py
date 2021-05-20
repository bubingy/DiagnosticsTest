# coding=utf-8

import os
from utils.conf import AzureQueryConf, WeeklyTestConf

from utils.azure import get_latest_acceptable_build,\
    get_artifact, get_artifact_version
from utils.github import get_pr_info


def get_tool_info():
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
    build = get_latest_acceptable_build(528, azure_conf.authorization)
    artifact = get_artifact(build, azure_conf.authorization)
    tool_version = get_artifact_version(artifact, azure_conf.authorization)
    pr_info = get_pr_info('dotnet', 'diagnostics', build['sourceVersion'])
    tool_feed = test_conf.tool_feed

    return tool_version, pr_info, tool_feed
