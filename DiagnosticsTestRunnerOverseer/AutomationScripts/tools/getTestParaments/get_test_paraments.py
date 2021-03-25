# coding=utf-8

from SDKVersion import get_sdk_version
from ToolVersion import get_latest_acceptable_build, \
    get_tool_version, get_artifact, get_pr_info


if __name__ == '__main__':
    sdk_version = get_sdk_version()
    print('Full version of sdk')
    for branch in sdk_version.keys():
        print(f'{branch}: {sdk_version[branch]}')
    
    build = get_latest_acceptable_build()
    tool_version = get_tool_version(
        get_artifact(build)
    )
    pr_info = get_pr_info(build)
    print('Info of tool')
    print(f'Version: {tool_version}')
    for key in pr_info.keys():
        print(f'{key}: {pr_info[key]}')