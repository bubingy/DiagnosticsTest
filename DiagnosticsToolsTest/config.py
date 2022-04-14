# coding=utf-8

import os
import base64
import configparser
from typing import Union

from utils.sysinfo import get_debugger, get_rid


class TestConfig:
    '''This class is used to store configuration and some global variables.
    
    '''
    def __init__(self, config: Union[os.PathLike, dict]=None):
        self.config = configparser.ConfigParser()
        self.work_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

        if config is None:
            config_file_path = os.path.join(self.work_dir, 'DiagnosticsToolsTest', 'config.conf')
            self.config.read(config_file_path)
        elif isinstance(config, os.PathLike) is True:
            config_file_path = config
            self.config.read(config_file_path)
        elif isinstance(config, dict) is True:
            self.config = config
        else:
            raise Exception("fail to read config!")
    
        self.rid = get_rid()
        self.debugger = get_debugger(self.rid)

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
        self.test_result = os.path.join(self.test_bed, 'TestResult')
        self.tool_root = os.path.join(self.test_bed, 'dotnet-tools')

        self.run_webapp = True
        self.run_consoleapp = True
        self.run_gcplayground = True
        if self.config['Test']['RunBenchmarks'] == 'true':
            self.run_benchmarks = True
        else: self.run_benchmarks = False
            
        # add environment variables
        dotnet_root = os.path.join(self.test_bed, '.dotnet-test')

        os.environ['DOTNET_ROOT'] = dotnet_root
        if 'win' in self.rid:
            os.environ['PATH'] = f'{dotnet_root};{self.tool_root};' + os.environ['PATH'] 
            self.dotnet = os.path.join(dotnet_root, 'dotnet.exe')
        else:
            os.environ['PATH'] = f'{dotnet_root}:{self.tool_root}:' + os.environ['PATH']
            self.dotnet = os.path.join(dotnet_root, 'dotnet')
