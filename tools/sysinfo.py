"""Provide system information"""

import re
import glob
import platform


def get_os_name() -> str|Exception:
    """get name of operation system
    
    :return: name of os or Exception if failed
    """
    system = platform.system().lower()
    if system == 'windows':
        os = 'win'
    elif system == 'linux':
        release_files = glob.glob('/etc/*release')
        content = ''
        for release_file in release_files:
            with open(release_file, 'r') as f:
                content += f.read().lower()
        if 'alpine' in content:
            os = 'linux-musl'
        else:
            os = 'linux'
    elif system== 'darwin':
        os = 'osx'
    else:
        os = Exception('unknown os')
    return os


def get_cpu_type() -> str|Exception:
    """get type of CPU
    
    :return: type of cpu or Exception if failed
    """
    machine_type = platform.machine().lower()
    if machine_type in ['x86_64', 'amd64']:
        cpu_arch = 'x64'
    elif machine_type in ['aarch64', 'arm64']:
        cpu_arch = 'arm64'
    elif machine_type in ['armv7l']:
        cpu_arch = 'arm'
    else:
        cpu_arch = Exception('unknown cpu')
    return cpu_arch


def get_rid() -> str|Exception:
    """Get .Net RID of current platform

    :return: .Net RID of current platform or Exception if failed
    """
    os_name = get_os_name()
    cpu_arch = get_cpu_type()
    if isinstance(os_name, Exception):
        return os_name
    if isinstance(cpu_arch, Exception):
        return cpu_arch
    else:
        return f'{os_name}-{cpu_arch}'


def get_debugger(rid: str) -> str|Exception:
    '''Get full name of debugger
    
    :param rid: `.Net RID` of current platform
    :Return: full name of debugger or Exception if failed
    '''
    if 'musl' in rid:
        return None
    elif 'win' in rid:
        debugger = 'cdb'
        return debugger
    else: # linux or osx
        if rid[-3:] == 'arm':
            debugger = '/root/lldb/bin/lldb'
            return debugger
        candidate_debuggers = glob.glob('/usr/bin/lldb*')
        if '/usr/bin/lldb' in candidate_debuggers:
            debugger = 'lldb'
            return debugger
        else:
            pattern = re.compile(r'/usr/bin/lldb-\d+')
            for candidate_debugger in candidate_debuggers:
                if pattern.match(candidate_debugger) is not None:
                    debugger = candidate_debugger.split('/')[-1]
                    return debugger
    return Exception('debugger not found')