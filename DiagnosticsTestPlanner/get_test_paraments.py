# coding=utf-8

from TestParaments.SDKVersion import get_sdk_version
from TestParaments.ToolInfo import ToolInfo


if __name__ == '__main__':
    sdk_version = get_sdk_version()
    print('Full version of sdk:')
    for branch in sdk_version.keys():
        print(f'{branch}: {sdk_version[branch]}')
    
    tool_info = ToolInfo()
    print('Info of tool:')
    print(f'Version: {tool_info.tool_version}')
    for key in tool_info.pr_info.keys():
        print(f'{key}: {tool_info.pr_info[key]}')