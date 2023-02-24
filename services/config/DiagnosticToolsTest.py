import os
import configparser

import instances.config.DiagnosticToolsTest as DiagToolTestConf
from services.sysinfo import get_rid, get_debugger


def load_diagtooltestconf(conf_file_path: os.PathLike=None) -> None:
    '''Load diagnostic tools test configuration from conf file

    :param conf_file_path: absolute path of conf file
    :return: None
    '''
    config = configparser.ConfigParser()

    config.read(conf_file_path)

    DiagToolTestConf.sdk_version = config['DotNet']['Version']
    DiagToolTestConf.sdk_buildid = config['DotNet']['BuildID']

    DiagToolTestConf.tool_version = config['DiagTool']['Version']
    DiagToolTestConf.tool_feed = config['DiagTool']['Feed']

    DiagToolTestConf.test_name = config['Test']['Name']
    DiagToolTestConf.testbed_root = config['Test']['TestBedRoot']
    DiagToolTestConf.use_container = config['Test']['Container']

    DiagToolTestConf.docker_base_url = config['Container']['DockerBaseUrl']
    DiagToolTestConf.dockerfile_url = config['Container']['DockerfileUrl']
    DiagToolTestConf.mount_dir = config['Container']['MountDir']
    DiagToolTestConf.security_opt = config['Container']['SecurityOpt']
    DiagToolTestConf.cap_add = config['Container']['CapAdd']
    DiagToolTestConf.privileged = config['Container']['Privileged']

    DiagToolTestConf.testbed = os.path.join(
        DiagToolTestConf.testbed_root,
        f'TestBed-{DiagToolTestConf.test_name}'
    )
    DiagToolTestConf.test_result_root = os.path.join(
        DiagToolTestConf.testbed,
        f'TestResult-{DiagToolTestConf.test_name}'
    )

    DiagToolTestConf.rid = get_rid()
    DiagToolTestConf.debugger = get_debugger(DiagToolTestConf.rid)

    DiagToolTestConf.tool_root = os.path.join(
        DiagToolTestConf.testbed,
        'diag-tools'
    )

    DiagToolTestConf.sdk_root = os.path.join(
        DiagToolTestConf.testbed, 'dotnet'
    )

    if 'win' in DiagToolTestConf.rid:
        bin_ext = '.exe'
        env_connector = ';'
    else:
        bin_ext = ''
        env_connector = ':'

    DiagToolTestConf.dotnet_bin_path = os.path.join(
        DiagToolTestConf.sdk_root,
        f'dotnet{bin_ext}'
    )

    DiagToolTestConf.env = os.environ.copy()
    DiagToolTestConf.env['DOTNET_ROOT'] = DiagToolTestConf.sdk_root
    DiagToolTestConf.env['PATH'] = \
        f'{DiagToolTestConf.sdk_root}{env_connector}{DiagToolTestConf.tool_root}{env_connector}' + DiagToolTestConf.env['PATH']