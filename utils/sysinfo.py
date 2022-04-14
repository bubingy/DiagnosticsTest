
import re
import glob
import platform


def get_rid():
    '''Get `.Net RID` of current platform.
    '''
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
        raise Exception(f'unsupported OS: {system}')
    
    machine_type = platform.machine().lower()
    if machine_type in ['x86_64', 'amd64']:
        rid = f'{os}-x64'
    elif machine_type in ['aarch64']:
        rid = f'{os}-arm64'
    elif machine_type in ['armv7l']:
        rid = f'{os}-arm'
    else:
        raise Exception(f'unsupported machine type: {machine_type}')

    return rid


def get_debugger(rid: str):
    '''Get full name of debugger.
    
    Args:
        rid - `.Net RID` of current platform.
    Return: full name of debugger.
    '''
    if 'musl' in rid:
        return ''
    elif 'win' in rid:
        debugger = 'cdb'
        return debugger
    else: # linux or osx
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

