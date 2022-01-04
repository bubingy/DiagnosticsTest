'''Load configuration
'''

# coding=utf-8

import os
import glob
import base64
import platform
import configparser


class TestConfig:
    '''This class is used to store configuration and some global variables.

    '''
    def __init__(self,
                 authorization: str,
                 sdk_version: str,
                 sdk_build_id: str,
                 runtime_version: str,
                 tool_version: str,
                 tool_feed: str,
                 test_bed: os.PathLike,
                 arch: str):
        self.work_dir = os.path.dirname(os.path.abspath(__file__))
        self.get_rid()
        self.authorization = authorization
        self.sdk_version = sdk_version
        self.sdk_build_id = sdk_build_id
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
            f'.dotnet-test{self.sdk_version}-{self.rid}-{arch}'
        )

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


class GlobalConfig:
    def __init__(self) -> None:
        self.config = configparser.ConfigParser()
        self.work_dir = os.path.dirname(os.path.abspath(__file__))
        config_file_path = os.path.join(self.work_dir, 'config.conf')

        self.config.read(config_file_path)

        self.sdk_version_list = self.config['SDK']['Version'].split('\n')
        self.sdk_version_list.remove('')

        self.sdk_build_id_list = self.config['SDK']['BuildID'].split('\n')
        self.sdk_build_id_list.remove('')

        self.runtime_version_list = self.config['Runtime']['Version'].split('\n')
        self.runtime_version_list.remove('')

        azure_pat = self.config['Azure']['PAT']
        self.authorization = str(
            base64.b64encode(bytes(f':{azure_pat}', 'ascii')),
            'ascii'
        )

        self.tool_version = self.config['Tool']['Version']
        self.tool_feed = self.config['Tool']['Feed']
        self.test_bed = self.config['Test']['TestBed']

        self.origin_ev = os.environ.copy()

    def get(self, index: int, arch: str):
        sdk_version, sdk_build_id, runtime_version = \
            self.sdk_version_list[index], self.sdk_build_id_list[index], self.runtime_version_list[index]

        test_conf = TestConfig(
            self.authorization,
            sdk_version,
            sdk_build_id,
            runtime_version,
            self.tool_version,
            self.tool_feed,
            self.test_bed,
            arch
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
