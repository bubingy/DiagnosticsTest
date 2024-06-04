import os
import configparser

from tools.sysinfo import SysInfo


class RunConfiguration:
    def __init__(self, test_bed: str, test_result_folder: str, dotnet_sdk_version: str):
        self.test_bed = test_bed
        self.dotnet_sdk_version = dotnet_sdk_version
        self.dotnet_root = os.path.join(test_bed, f'dotnet-sdk{dotnet_sdk_version}')
        self.dotnet_bin_path = os.path.join(self.dotnet_root, f'dotnet{SysInfo.bin_ext}')
        self.test_result_folder = test_result_folder

        env = os.environ.copy()
        env['DOTNET_ROOT'] = self.dotnet_root
        env['PATH'] = f'{self.dotnet_root}{SysInfo.env_connector}' + env['PATH']

        # environment variable
        self.env: dict = env

class LTTngTestConfiguration:
    def __init__(self, conf_file_path: str):
        self.__parse_conf_file(conf_file_path)

        self.conf_file_path = conf_file_path
        self.test_name = f'LTTng-{self.os_name}-{self.cpu_arch}'
        self.test_bed = os.path.join(self.testbed_root, f'Testbed-{self.test_name}')
        self.test_result_folder = os.path.join(self.test_bed, f'TestResult-{self.test_name}')

        self.run_conf_list: list[RunConfiguration] = list()
        for sdk_version in self.dotnet_sdk_version_list:
            self.run_conf_list.append(
                RunConfiguration(self.test_bed, self.test_result_folder, sdk_version)
            )

    def __parse_conf_file(self, conf_file_path: str) -> None:
        '''Parse configuration file 
        
        :param conf_file_path: path to configuration file
        :return: LTTngTestConfiguration instance or Exception
        '''
        try:
            config = configparser.ConfigParser()
            config.read(conf_file_path)
            # DotNet section
            self.dotnet_sdk_version_list: str = config['DotNet']['Version'].splitlines()
            if '' in self.dotnet_sdk_version_list:
                self.dotnet_sdk_version_list.remove('')

            # Test section
            self.os_name: str = config['Test']['OSName']
            self.cpu_arch: str = config['Test']['CPUArchitecture']
            self.testbed_root: str = config['Test']['TestBedRoot']

        except Exception as ex:
            raise Exception(f'fail to parse conf file {conf_file_path}: {ex}')    