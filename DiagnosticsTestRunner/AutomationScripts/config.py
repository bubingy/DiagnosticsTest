# coding=utf-8

import json
import os


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
        self.rid = self.config['Platform']['RID']
        self.debugger = self.config['Platform']['Debugger']
        self.sdk_version = self.config['SDK']['Version']
        self.tool_version = self.config['Tool']['Version']
        self.tool_commit = self.config['Tool']['Commit']
        self.tool_feed = self.config['Tool']['Feed']
        self.test_bed = self.config['Test']['TestBed']
        if self.config['Test']['RunBenchmarks'] == 'true':
            self.run_benchmarks = True
        else:
            self.run_benchmarks = False
            
        self.test_result = os.path.join(
            self.test_bed,
            'TestResult' + self.config['Test']['ID']
        )
        self.tool_root = os.path.dirname(os.path.abspath(__file__))

        dotnet_root = os.path.join(self.test_bed, '.dotnet-test')
        tool_root = os.path.join(os.environ['HOME'], '.dotnet', 'tools')
        os.environ['DOTNET_ROOT'] = dotnet_root
        if 'win' in self.rid:
            os.environ['PATH'] = f'{dotnet_root};{tool_root};' + os.environ['PATH'] 
        else:
            os.environ['PATH'] = f'{dotnet_root}:{tool_root}:' + os.environ['PATH']

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


configuration = GlobalConfig()
