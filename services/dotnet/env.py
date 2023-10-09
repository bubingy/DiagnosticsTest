import os

from services.sysinfo import get_os_name

def create_env_activation_script(dotnet_root: os.PathLike,
                                tool_root: os.PathLike, 
                                output: os.PathLike) -> None:
    os_name = get_os_name()
    if os_name == 'win':
        lines = [
            f'$Env:DOTNET_ROOT={dotnet_root}',
            f'$Env:Path+=;{dotnet_root}',
            f'$Env:Path+=;{tool_root}'
        ]
    else:
        lines = [
            f'export DOTNET_ROOT={dotnet_root}',
            f'export PATH=$PATH:{dotnet_root}',
            f'export PATH=$PATH:{tool_root}'
        ]
    
    with open(output, 'w+') as fs:
        fs.writelines(lines)