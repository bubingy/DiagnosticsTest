'''Load configuration
'''

import os
import configparser

from utils.sysinfo import get_rid


class TestConfig:
    '''This class is used to store configuration and some global variables.

    '''
    def __init__(self,
                 sdk_version: str,
                 runtime_version: str,
                 arch: str,
                 tool_version: str,
                 tool_feed: str,
                 test_bed: os.PathLike):
        self.work_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.rid = get_rid()
        self.sdk_version = sdk_version
        self.runtime_version = runtime_version
        self.tool_version = tool_version
        self.tool_feed = tool_feed
        self.test_bed = test_bed
        self.dump_directory = os.path.join(
            self.test_bed,
            f'dumpfiles-dotnet{self.sdk_version}'
        )
        self.analyze_output = os.path.join(
            self.test_bed,
            f'analyzeoutput-dotnet{self.sdk_version}'
        )
        self.tool_root = os.path.join(
            self.test_bed,
            f'tools-dotnet{self.sdk_version}-{arch}'
        )
        self.dotnet_root = os.path.join(
            self.test_bed,
            f'.dotnet-test{self.sdk_version}-{arch}'
        )
        self.dotnet = os.path.join(self.dotnet_root, 'dotnet')


class GlobalConfig:
    def __init__(self) -> None:
        self.config = configparser.ConfigParser()
        self.work_dir = os.path.dirname(os.path.abspath(__file__))
        config_file_path = os.path.join(self.work_dir, 'config.conf')

        self.config.read(config_file_path)

        self.sdk_version_list = self.config['SDK']['Version'].split('\n')
        self.sdk_version_list.remove('')
        
        self.runtime_version_list = self.config['Runtime']['Version'].split('\n')
        self.runtime_version_list.remove('')

        self.tool_version = self.config['Tool']['Version']
        self.tool_feed = self.config['Tool']['Feed']
        self.test_bed = self.config['Test']['TestBed']

        self.origin_ev = os.environ.copy()

    def get(self, index: int, arch: str):
        sdk_version, runtime_version = \
            self.sdk_version_list[index], self.runtime_version_list[index]

        test_conf = TestConfig(
            sdk_version,
            runtime_version,
            arch,
            self.tool_version,
            self.tool_feed,
            self.test_bed
        )

        os.environ['DOTNET_ROOT'] = test_conf.dotnet_root

        if 'win' in test_conf.rid: connector = ';'
        else: connector = ':'

        os.environ['PATH'] = connector.join(
            [
                test_conf.dotnet_root,
                test_conf.tool_root,
                self.origin_ev['PATH']
            ]
        )
        return test_conf
