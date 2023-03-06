import os
import configparser

import instances.config.LTTngTest as LTTngTestConf
from services.sysinfo import get_rid


def load_lttngtestconf(conf_file_path: os.PathLike=None) -> None:
    '''Load diagnostic tools test configuration from conf file

    :param conf_file_path: absolute path of conf file
    :return: None
    '''
    config = configparser.ConfigParser()

    config.read(conf_file_path)

    LTTngTestConf.sdk_version_list = config['DotNet']['Version'].split('\n')
    LTTngTestConf.sdk_version_list.remove('')
    LTTngTestConf.sdk_buildid_list = config['DotNet']['BuildID'].split('\n')
    LTTngTestConf.sdk_buildid_list.remove('')

    LTTngTestConf.test_name = config['Test']['Name']
    LTTngTestConf.testbed_root = config['Test']['TestBedRoot']
    LTTngTestConf.use_container = config['Test']['Container']

    LTTngTestConf.docker_base_url = config['Container']['DockerBaseUrl']
    LTTngTestConf.dockerfile_url = config['Container']['DockerfileUrl']
    LTTngTestConf.mount_dir = config['Container']['MountDir']
    LTTngTestConf.security_opt = config['Container']['SecurityOpt']
    LTTngTestConf.cap_add = config['Container']['CapAdd']
    LTTngTestConf.privileged = config['Container']['Privileged']

    LTTngTestConf.testbed = os.path.join(
        LTTngTestConf.testbed_root,
        f'TestBed-{LTTngTestConf.test_name}'
    )
    LTTngTestConf.test_result_root = os.path.join(
        LTTngTestConf.testbed,
        f'TestResult-{LTTngTestConf.test_name}'
    )

    LTTngTestConf.rid = get_rid()

    LTTngTestConf.env = os.environ.copy()