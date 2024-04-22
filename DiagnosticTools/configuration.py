import os
import configparser

from tools.sysinfo import SysInfo


class DiagToolsTestConfiguration:
    def __init__(self, conf_file_path: str):
        self.__parse_conf_file(conf_file_path)

        self.test_name = f'{SysInfo.os_name}-{SysInfo.cpu_arch}-.NET{self.dotnet_sdk_version}-Tool{self.diag_tool_version}'
        self.test_bed = os.path.join(self.testbed_root, f'Testbed-{self.test_name}{self.optional_feature_container_flag}')
        self.test_result_folder = os.path.join(self.test_bed, f'TestResult-{self.test_name}{self.optional_feature_container_flag}')

        self.dotnet_root = os.path.join(self.test_bed, 'dotnet-sdk')
        self.dotnet_bin_path = os.path.join(self.dotnet_root, f'dotnet{SysInfo.bin_ext}')

        self.diag_tool_root = os.path.join(self.test_bed, f'diag-tool')

        env = os.environ.copy()
        env['DOTNET_ROOT'] = self.dotnet_root
        env['PATH'] = f'{self.dotnet_root}{SysInfo.env_connector}{self.diag_tool_root}{SysInfo.env_connector}' + env['PATH']

        # environment variable
        self.env: dict = env
    
    def __parse_conf_file(self, conf_file_path: str) -> None:
        """Parse configuration file 
        
        :param conf_file_path: path to configuration file
        :return: DiagToolsTestConfiguration instance or Exception
        """
        try:
            config = configparser.ConfigParser()
            config.read(conf_file_path)
            # DotNet section
            self.dotnet_sdk_version: str = config['DotNet']['Version']
            self.app_to_create: list[str] = config['DotNet']['CreateApps'].splitlines()
            self.app_to_create.remove('')

            # DiagTool section
            self.diag_tool_version: str = config['DiagTool']['Version']
            self.diag_tool_to_install: list[str] = config['DiagTool']['InstallTools'].splitlines()
            self.diag_tool_to_install.remove('')
            self.diag_tool_to_test: list[str] = config['DiagTool']['TestTools'].splitlines()
            self.diag_tool_to_install.remove('')
            self.diag_tool_feed: str = config['DiagTool']['Feed']

            # Test section
            self.os_name: str = config['Test']['OSName']
            self.cpu_arch: str = config['Test']['CPUArchitecture']
            self.testbed_root: str = config['Test']['TestBedRoot']

            if config['Test']['OptionalFeatureContainer'].lower() in ['yes', 'y']:
                self.optional_feature_container = True
                self.optional_feature_container_flag = '-NO'
            else:
                self.optional_feature_container = False
                self.optional_feature_container_flag = ''
                
        except Exception as ex:
            raise Exception(f'fail to parse conf file {conf_file_path}: {ex}')    
        

    # def __parse_json_file(conf_file_path: str) -> None:
