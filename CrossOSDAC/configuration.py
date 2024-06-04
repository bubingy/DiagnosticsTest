import os
import configparser

from tools.sysinfo import SysInfo


class RunConfiguration:
    def __init__(self, 
                 test_bed: str, 
                 dotnet_sdk_version: str, 
                 diag_tool_version: str,
                 diag_tool_feed: str,
                 arch: str=None) -> None:
        self.test_bed = test_bed
        self.dotnet_sdk_version = dotnet_sdk_version
        self.dotnet_root = os.path.join(test_bed, f'dotnet-sdk{dotnet_sdk_version}')
        self.dotnet_bin_path = os.path.join(self.dotnet_root, f'dotnet{SysInfo.bin_ext}')

        self.diag_tool_version = diag_tool_version
        self.diag_tool_root = os.path.join(self.test_bed, f'diag-tool-.NET{dotnet_sdk_version}')
        self.diag_tool_feed = diag_tool_feed

        self.arch = arch

        self.dump_folder = os.path.join(test_bed, f'dumps-net{dotnet_sdk_version}')
        self.analyze_folder = os.path.join(test_bed, f'analyze-net{dotnet_sdk_version}')
        
        env = os.environ.copy()
        env['DOTNET_ROOT'] = self.dotnet_root
        env['PATH'] = f'{self.dotnet_root}{SysInfo.env_connector}{self.diag_tool_root}{SysInfo.env_connector}' + env['PATH']

        # environment variable
        self.env: dict = env


class CrossOSDACConfiguration:
    def __init__(self, conf_file_path: str):
        self.__parse_conf_file(conf_file_path)

        self.conf_file_path = conf_file_path
        self.test_name = f'CrossOSDAC-{self.os_name}-{self.cpu_arch}-{self.diag_tool_version}'
        self.analyze_testbed: str = os.path.join(self.testbed_root, f'TestBed-{self.test_name}')

        self.run_conf_list: list[RunConfiguration] = list()

        for sdk_version in self.dotnet_sdk_version_list:
            if 'win' in SysInfo.rid:
                arch_list = ['x86', 'x64']
                test_bed = self.validate_testbed
            else:
                arch_list = [None]
                test_bed = self.analyze_testbed
            for arch in arch_list:
                self.run_conf_list.append(
                    RunConfiguration(
                        test_bed,
                        sdk_version,
                        self.diag_tool_version,
                        self.diag_tool_feed,
                        arch
                    )
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
            self.validate_testbed: str = config['Test']['TestBed']

        except Exception as ex:
            raise Exception(f'fail to parse conf file {conf_file_path}: {ex}') 
   