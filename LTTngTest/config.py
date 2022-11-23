'''Load configuration
'''

# coding=utf-8

import os
import base64
import configparser

from utils.sysinfo import get_rid


class TestConfig:
    '''This class is used to store configuration and some global variables.

    '''
    def __init__(self,
                 authorization: str,
                 sdk_version: str,
                 sdk_build_id: str,
                 test_bed: os.PathLike):
        self.work_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.rid = get_rid()
        self.authorization = authorization
        self.sdk_version = sdk_version
        self.sdk_build_id = sdk_build_id
        self.test_bed = test_bed
        self.trace_directory = os.path.join(
            self.test_bed,
            f'tracefiles'
        )
        self.dotnet_root = os.path.join(
            self.test_bed,
            f'.dotnet-test-{self.sdk_version}-{self.rid}'
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

        self.sdk_build_id_list = self.config['SDK']['BuildID'].split('\n')
        self.sdk_build_id_list.remove('')

        azure_pat = self.config['Azure']['PAT']
        self.authorization = str(
            base64.b64encode(bytes(f':{azure_pat}', 'ascii')),
            'ascii'
        )

        self.test_bed = self.config['Test']['TestBed']

        self.origin_ev = os.environ.copy()

    def get(self, index: int):
        sdk_version = self.sdk_version_list[index]
        if len(self.sdk_build_id_list) != 0:
            sdk_build_id = self.sdk_build_id_list[index]
        else:
            sdk_build_id = ''
            
        test_conf = TestConfig(
            self.authorization,
            sdk_version,
            sdk_build_id,
            self.test_bed
        )

        os.environ['DOTNET_ROOT'] = test_conf.dotnet_root

        if 'win' in test_conf.rid: connector = ';'
        else: connector = ':'

        os.environ['PATH'] = connector.join(
            [
                test_conf.dotnet_root,
                self.origin_ev['PATH']
            ]
        )
        return test_conf
