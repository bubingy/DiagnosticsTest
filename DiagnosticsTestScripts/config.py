# coding=utf-8

import os
import re
import glob
import platform
import configparser


class GlobalConfig:
    '''This class is used to store configuration and some global variables.
    
    '''
    def __init__(self):
        self.config = configparser.ConfigParser()
        self.work_dir = os.path.dirname(os.path.abspath(__file__))
        config_file_path = os.path.join(self.work_dir, 'config.conf')

        self.config.read(config_file_path)
        self.rid = self.get_rid()
        self.debugger = self.get_debugger()
        self.sdk_version = self.config['SDK']['Version']
        self.tool_version = self.config['Tool']['Version']
        self.tool_commit = self.config['Tool']['Commit']
        self.tool_feed = self.config['Tool']['Feed']
        self.test_bed = self.config['Test']['TestBed']
        if self.config['Test']['RunBenchmarks'] == 'true':
            self.run_benchmarks = True
        else:
            self.run_benchmarks = False
            
        self.test_result = os.path.join(self.test_bed, 'TestResult')
        self.tool_root = os.path.dirname(os.path.abspath(__file__))

        self.webappapp_runnable = True
        self.consoleapp_runnable = True
        self.gcplayground_runnable = True

        self.check_init_config()

    def check_init_config(self):
        '''Check configuration and create directories if necessary

        '''
        assert self.rid in [
            'win-x64', 'osx-x64', 'linux-x64', 
            'linux-musl-x64', 'linux-arm', 'linux-arm64'
        ]
        try:
            if os.path.exists(self.test_bed) is False:
                os.makedirs(self.test_bed)
        except Exception as e:
            print(e)
            exit(-1)
        
        if os.path.exists(self.test_result) is False:
            os.makedirs(self.test_result)

    def get_rid(self) -> str:
        '''Get `.Net RID` of current platform.

        Return: `.Net RID` of current platform.
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

        return rid


    def get_debugger(self) -> str:
        '''Get full name of debugger.
        
        Args:
            rid - `.Net RID` of current platform.
        Return: full name of debugger.
        '''
        if 'musl' in self.rid:
            return ''
        elif 'win' in self.rid:
            return 'cdb'
        else: # linux or osx
            candidate_debuggers = glob.glob('/usr/bin/lldb*')
            if '/usr/bin/lldb' in candidate_debuggers:
                return 'lldb'
            else:
                pattern = re.compile(r'/usr/bin/lldb-\d+')
                for candidate_debugger in candidate_debuggers:
                    if pattern.match(candidate_debugger) is not None:
                        return candidate_debugger.split('/')[-1]


configuration = GlobalConfig()
