'''Load configuration
'''

# coding=utf-8

import os
import sys
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
        self.sdk_version = self.config['SDK']['Version']
        self.runtime_version = self.config['Runtime']['Version']
        self.tool_version = self.config['Tool']['Version']
        self.tool_feed = self.config['Tool']['Feed']
        self.test_bed = self.config['Test']['TestBed']
        self.dump_directory = os.path.join(self.test_bed, 'dumpfiles')
        self.analyze_output = os.path.join(self.test_bed, 'analyzeoutput')

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


configuration = GlobalConfig()
