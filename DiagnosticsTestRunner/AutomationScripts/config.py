# coding=utf-8

import re
import os
import glob
import platform


class GlobalConfig:
    '''This class is used to store configuration and some global variables.
    
    '''
    def __init__(self, test_config: dict):
        self.work_dir = os.path.dirname(os.path.abspath(__file__))

        self.get_rid()
        self.get_debugger()
        self.os_name = test_config['OS']
        self.sdk_version = test_config['SDK']
        self.tool_version = test_config['Tool_Info']['version']
        self.tool_commit = test_config['Tool_Info']['commit']
        self.tool_feed = test_config['Tool_Info']['feed']
        self.test_bed = test_config['Test']['TestBed']
        self.run_benchmarks = test_config['Test']['RunBenchmarks']

        self.test_result = os.path.join(
            self.test_bed,
            f'TestResult-{self.os_name}' 
        )
        self.tool_root = os.path.dirname(os.path.abspath(__file__))

        dotnet_root = os.path.join(self.test_bed, '.dotnet-test')

        # if 'win' in self.rid: home_path = os.environ['USERPROFILE']
        # else: home_path = os.environ['HOME']
        # diagnostics_tool_root = os.path.join(home_path, '.dotnet', 'tools')
        os.environ['DOTNET_ROOT'] = dotnet_root
        if 'win' in self.rid:
            os.environ['PATH'] = f'{dotnet_root};{self.tool_root};' + os.environ['PATH'] 
        else:
            os.environ['PATH'] = f'{dotnet_root}:{self.tool_root}:' + os.environ['PATH']

        self.webappapp_runnable = True
        self.consoleapp_runnable = True
        self.gcplayground_runnable = True

    def get_rid(self):
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
            raise f'unsupported OS: {system}'
        
        machine_type = platform.machine().lower()
        if machine_type in ['x86_64', 'amd64']:
            rid = f'{os}-x64'
        elif machine_type in ['aarch64']:
            rid = f'{os}-arm64'
        elif machine_type in ['armv7l']:
            rid = f'{os}-arm'
        else:
            raise f'unsupported machine type: {machine_type}'

        self.rid = rid


    def get_debugger(self):
        '''Get full name of debugger.
        
        Args:
            rid - `.Net RID` of current platform.
        Return: full name of debugger.
        '''
        if 'musl' in self.rid:
            return ''
        elif 'win' in self.rid:
            self.debugger = 'cdb'
            return
        else: # linux or osx
            candidate_debuggers = glob.glob('/usr/bin/lldb*')
            if '/usr/bin/lldb' in candidate_debuggers:
                self.debugger = 'lldb'
                return
            else:
                pattern = re.compile(r'/usr/bin/lldb-\d+')
                for candidate_debugger in candidate_debuggers:
                    if pattern.match(candidate_debugger) is not None:
                        self.debugger = candidate_debugger.split('/')[-1]
                        return


configuration = None
