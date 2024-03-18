import os
import configparser

from tools import sysinfo

class DiagToolsTestConfiguration:
    def __init__(self,
                dotnet_sdk_version: str,
                dotnet_root: str,
                dotnet_bin_path: str,
                app_to_create: list[str],
                app_to_build: list[str],
                diag_tool_version: str,
                diag_tool_to_install: list[str],
                diag_tool_to_test: list[str],
                diag_tool_feed: str,
                diag_tool_root: str,
                testbed: str,
                test_result_folder: str,
                debugger: str,
                rid: str,
                optional_feature_container: bool,
                env: dict) -> None:
        # DotNet section
        self.dotnet_sdk_version: str = dotnet_sdk_version
        self.dotnet_root: str = dotnet_root
        self.dotnet_bin_path: str = dotnet_bin_path
        self.app_to_create = app_to_create
        self.app_to_build = app_to_build

        # DiagTool section
        self.diag_tool_version: str = diag_tool_version
        self.diag_tool_to_install: list[str] = diag_tool_to_install
        self.diag_tool_to_test: list[str] = diag_tool_to_test
        self.diag_tool_feed: str = diag_tool_feed
        self.diag_tool_root: str = diag_tool_root

        # Test section
        self.testbed: str = testbed
        self.test_result_folder: str = test_result_folder
        self.debugger: str = debugger
        self.rid: str = rid
        self.optional_feature_container: bool = optional_feature_container

        # environment variable
        self.env: dict = env
    
def parse_conf_file(conf_file_path: str) -> list[DiagToolsTestConfiguration]:
    config = configparser.ConfigParser()
    config.read(conf_file_path)
    
    # DotNet section
    dotnet_sdk_version: str = config['DotNet']['Version']
    app_to_create: list[str] = config['DotNet']['CreateApps'].splitlines()
    app_to_create.remove('')
    app_to_build: list[str] = config['DotNet']['BuildApps'].splitlines()
    app_to_build.remove('')

    # DiagTool section
    diag_tool_version: str = config['DiagTool']['Version']
    diag_tool_to_install: list[str] = config['DiagTool']['InstallTools'].splitlines()
    diag_tool_to_install.remove('')
    diag_tool_to_test: list[str] = config['DiagTool']['TestTools'].splitlines()
    diag_tool_to_install.remove('')
    diag_tool_feed: str = config['DiagTool']['Feed']

    # Test section
    os_name: str = config['Test']['OSName']
    cpu_arch: str = config['Test']['CPUArchitecture']
    testbed_root: str = config['Test']['TestBedRoot']

    rid = sysinfo.get_rid()
    debugger  = sysinfo.get_debugger(rid)

    if 'win' in rid:
        bin_ext = '.exe'
        env_connector = ';'
    else:
        bin_ext = ''
        env_connector = ':'

    if config['Test']['OptionalFeatureContainer'].lower() in ['yes', 'y']:
        optional_feature_container = True
        optional_feature_container_flag = 'NO'
    else:
        optional_feature_container = False
        optional_feature_container_flag = ''

    test_name = f'{os_name}-{cpu_arch}-.NET{dotnet_sdk_version}-Tool{diag_tool_version}'
    test_bed = os.path.join(testbed_root, f'Testbed-{test_name}-{optional_feature_container_flag}')
    test_result_folder = os.path.join(test_bed, f'TestResult-{test_name}-{optional_feature_container_flag}')

    dotnet_root = os.path.join(test_bed, 'dotnet-sdk')
    dotnet_bin_path = os.path.join(dotnet_root, f'dotnet{bin_ext}')

    diag_tool_root = os.path.join(test_bed, f'diag-tool')

    env = os.environ.copy()
    env['DOTNET_ROOT'] = dotnet_root
    env['PATH'] = f'{dotnet_root}{env_connector}{diag_tool_root}{env_connector}' + env['PATH']

    return DiagToolsTestConfiguration(
        dotnet_sdk_version,
        dotnet_root,
        dotnet_bin_path,
        app_to_create,
        app_to_build,
        diag_tool_version,
        diag_tool_to_install,
        diag_tool_to_test,
        diag_tool_feed,
        diag_tool_root,
        test_bed,
        test_result_folder,
        debugger,
        rid,
        optional_feature_container,
        env
    )
