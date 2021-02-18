# coding=utf-8

import os
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


configuration = GlobalConfig()
