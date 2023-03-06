import os
import configparser

import instances.config.CrossOSDACTest as CrossOSDACTestConf
from services.sysinfo import get_rid


def load_crossosdactestconf(conf_file_path: os.PathLike=None) -> None:
    '''Load diagnostic tools test configuration from conf file

    :param conf_file_path: absolute path of conf file
    :return: None
    '''
    config = configparser.ConfigParser()

    config.read(conf_file_path)

    CrossOSDACTestConf.sdk_version_list = config['DotNet']['Version'].split('\n')
    CrossOSDACTestConf.sdk_version_list.remove('')
    CrossOSDACTestConf.sdk_buildid_list = config['DotNet']['BuildID'].split('\n')
    CrossOSDACTestConf.sdk_buildid_list.remove('')

    CrossOSDACTestConf.tool_version = config['DiagTool']['Version']
    CrossOSDACTestConf.tool_feed = config['DiagTool']['Feed']

    CrossOSDACTestConf.test_name = config['Test']['Name']

    CrossOSDACTestConf.analyze_testbed_root = config['Analyze']['TestBedRoot']
    CrossOSDACTestConf.use_container = config['Analyze']['Container']

    CrossOSDACTestConf.validate_testbed = config['Validate']['TestBed']

    CrossOSDACTestConf.docker_base_url = config['Container']['DockerBaseUrl']
    CrossOSDACTestConf.dockerfile_url = config['Container']['DockerfileUrl']
    CrossOSDACTestConf.mount_dir = config['Container']['MountDir']
    CrossOSDACTestConf.security_opt = config['Container']['SecurityOpt']
    CrossOSDACTestConf.cap_add = config['Container']['CapAdd']
    CrossOSDACTestConf.privileged = config['Container']['Privileged']

    CrossOSDACTestConf.analyze_testbed = os.path.join(
        CrossOSDACTestConf.analyze_testbed_root,
        f'TestBed-{CrossOSDACTestConf.test_name}'
    )

    CrossOSDACTestConf.rid = get_rid()

    CrossOSDACTestConf.env = os.environ.copy()