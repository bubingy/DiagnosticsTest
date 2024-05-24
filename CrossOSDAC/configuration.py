import os
import configparser

from tools.sysinfo import SysInfo


class AnalyzeRunConfiguration:
    def __init__(self, testbed_root: str, dotnet_sdk_version: str, diag_tool_version: str) -> None:
        pass


class ValidateRunConfiguration:
    def __init__(self, testbed: str, dotnet_sdk_version: str, diag_tool_version: str) -> None:
        pass


class CrossOSDACConfiguration:
    def __init__(self, conf_file_path: str):
        self.__parse_conf_file(conf_file_path)

        self.conf_file_path = conf_file_path
        self.test_name = f'{self.os_name}-{self.cpu_arch}-{self.diag_tool_version}'

        self.analyze_run_conf_list: list[AnalyzeRunConfiguration] = list()
        self.validate_run_conf_list: list[ValidateRunConfiguration] = list()

        for sdk_version in self.dotnet_sdk_version_list:
            self.analyze_run_conf_list.append(
                AnalyzeRunConfiguration(self.testbed_root, sdk_version, self.diag_tool_version)
            )
            self.validate_run_conf_list.append(
                ValidateRunConfiguration(self.testbed, sdk_version, self.diag_tool_version)
            )

    def __parse_conf_file(self, conf_file_path: str) -> None:
        '''Parse configuration file 
        
        :param conf_file_path: path to configuration file
        :return: CrossOSDACTestConfiguration instance or Exception
        '''
        try:
            config = configparser.ConfigParser()
            config.read(conf_file_path)
            # DotNet section
            self.dotnet_sdk_version_list: str = config['DotNet']['Version'].splitlines()
            if '' in self.dotnet_sdk_version_list:
                self.dotnet_sdk_version_list.remove('')

            # DiagTool section
            self.diag_tool_version: str = config['DiagTool']['Version']
            self.diag_tool_feed: str = config['DiagTool']['Feed']

            # Test section
            self.os_name: str = config['Test']['OSName']
            self.cpu_arch: str = config['Test']['CPUArchitecture']
            self.testbed_root: str = config['Test']['TestBedRoot']
            self.testbed: str = config['Test']['TestBed']

        except Exception as ex:
            raise Exception(f'fail to parse conf file {conf_file_path}: {ex}')    