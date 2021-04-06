# coding=utf-8

from datetime import datetime

from OSRotation import get_os_rotation
from TestParaments.SDKVersion import get_sdk_version
from TestParaments.ToolInfo import ToolInfo


if __name__ == '__main__':
    print('OS ratation:')
    print(
        get_os_rotation(
            datetime.today().strftime('%Y-%m-%d')
        )
    )
    sdk_version = get_sdk_version()
    print('Full version of sdk:')
    for branch in sdk_version.keys():
        if branch[0] == '3':
            dotnet_prefix = '.net core'
        else:
            dotnet_prefix = '.net'
        print(f'{dotnet_prefix} {branch}: {sdk_version[branch]}')
    
    tool_info = ToolInfo()
    print('Info of tool:')
    print(f'Version: {tool_info.tool_version}')
    for key in tool_info.pr_info.keys():
        print(f'{key}: {tool_info.pr_info[key]}')