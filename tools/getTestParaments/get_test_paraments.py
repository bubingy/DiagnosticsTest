# coding=utf-8

from SDKVersion import get_sdk_version
from ToolInfo import ToolInfo


if __name__ == '__main__':
    sdk_version = get_sdk_version()
    print('Full version of sdk')
    for branch in sdk_version.keys():
        print(f'{branch}: {sdk_version[branch]}')
    
    tool_info = ToolInfo()
    build = tool_info.build
    tool_version = tool_info.tool_version
    pr_info = tool_info.pr_info
    print('Info of tool')
    print(f'Version: {tool_version}')
    for key in pr_info.keys():
        print(f'{key}: {pr_info[key]}')