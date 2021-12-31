# coding=utf-8

import os
import re
import glob
import base64
import platform
import configparser
from typing import Union


class TestConfig:
    '''This class is used to store configuration and some global variables.
    
    '''
    def __init__(self, config: Union[os.PathLike, dict]=None):
        self.config = configparser.ConfigParser()
        self.work_dir = os.path.dirname(os.path.abspath(__file__))

        if config is None:
            config_file_path = os.path.join(self.work_dir, 'config.conf')
            self.config.read(config_file_path)
        elif isinstance(config, os.PathLike) is True:
            config_file_path = config
            self.config.read(config_file_path)
        elif isinstance(config, dict) is True:
            self.config = config
        else:
            raise "fail to read config!"
    
        self.__get_rid()
        self.__get_debugger()

        azure_pat = self.config['Azure']['PAT']
        self.authorization = str(
            base64.b64encode(bytes(f':{azure_pat}', 'ascii')),
            'ascii'
        )
        
        self.sdk_version = self.config['SDK']['Version']
        self.sdk_build_id = self.config['SDK']['BuildID']
        self.source_feed = self.config['SDK']['Feed']
        self.tool_version = self.config['Tool']['Version']
        self.tool_commit = self.config['Tool']['Commit']
        self.tool_feed = self.config['Tool']['Feed']

        self.test_bed = self.config['Test']['TestBed']
        self.run_benchmarks = True
        self.run_webapp = True
        self.run_consoleapp = True
        self.run_gcplayground = True
        if self.config['Test']['RunBenchmarks'] == 'true':
            self.run_benchmarks = True
        else: self.run_benchmarks = False
            
        self.test_result = os.path.join(self.test_bed, 'TestResult')
        self.tool_root = os.path.join(self.test_bed, 'dotnet-tools')
        # add environment variables
        dotnet_root = os.path.join(self.test_bed, '.dotnet-test')

        os.environ['DOTNET_ROOT'] = dotnet_root
        if 'win' in self.rid:
            os.environ['PATH'] = f'{dotnet_root};{self.tool_root};' + os.environ['PATH'] 
        else:
            os.environ['PATH'] = f'{dotnet_root}:{self.tool_root}:' + os.environ['PATH']

    def prepare_test_bed(self):
        '''Create folders for TestBed and TestResult.
        '''
        try:
            if not os.path.exists(configuration.test_bed):
                os.makedirs(configuration.test_bed)
            if not os.path.exists(configuration.test_result):
                os.makedirs(configuration.test_result)
        except Exception as e:
            print(f'fail to create folders for TestBed and TestResult: {e}')
            exit(-1)

    def __get_rid(self):
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


    def __get_debugger(self):
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


configuration: TestConfig = None
