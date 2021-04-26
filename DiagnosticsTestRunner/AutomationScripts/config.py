# coding=utf-8

import re
import os
import json
import glob
import platform


class GlobalConfig:
    '''This class is used to store configuration and some global variables.
    
    '''
    def __init__(self):
        self.work_dir = os.path.dirname(os.path.abspath(__file__))

        config_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            'config.json'
        )
        with open(config_path, 'r') as f:
            self.config = json.load(f)

        self.get_rid()
        self.get_debugger()
        self.sdk_version = self.config['SDK']
        self.tool_version = self.config['Tool_Info']['version']
        self.tool_commit = self.config['Tool_Info']['commit']
        self.tool_feed = self.config['Tool_Info']['feed']
        self.test_bed = self.config['Test']['TestBed']
        if self.config['Test']['RunBenchmarks'] == 'true':
            self.run_benchmarks = True
        else:
            self.run_benchmarks = False
            
        self.test_result = os.path.join(
            self.test_bed,
            'TestResult'
        )
        self.tool_root = os.path.dirname(os.path.abspath(__file__))

        dotnet_root = os.path.join(self.test_bed, '.dotnet-test')

        if 'win' in self.rid: home_path = os.environ['USERPROFILE']
        else: home_path = os.environ['HOME']
        diagnostics_tool_root = os.path.join(home_path, '.dotnet', 'tools')
        os.environ['DOTNET_ROOT'] = dotnet_root
        if 'win' in self.rid:
            os.environ['PATH'] = f'{dotnet_root};{diagnostics_tool_root};' + os.environ['PATH'] 
        else:
            os.environ['PATH'] = f'{dotnet_root}:{diagnostics_tool_root}:' + os.environ['PATH']

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


configuration = GlobalConfig()
