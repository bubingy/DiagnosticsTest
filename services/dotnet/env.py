import os

from services.sysinfo import get_os_name

def create_env_activation_script(dotnet_root: os.PathLike,
                                tool_root: os.PathLike, 
                                output: os.PathLike) -> None:
    os_name = get_os_name()
    if os_name == 'win':
        lines = [
            f'$Env:DOTNET_ROOT={dotnet_root}\n',
            f'$Env:Path+=;{dotnet_root}\n',
            f'$Env:Path+=;{tool_root}\n'
        ]
    else:
        lines = [
            f'export DOTNET_ROOT={dotnet_root}\n',
            f'export PATH=$PATH:{dotnet_root}\n',
            f'export PATH=$PATH:{tool_root}\n'
        ]
    
    with open(output, 'w+') as fs:
        fs.writelines(lines)