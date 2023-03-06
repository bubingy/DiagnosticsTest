import os
import shutil

import docker

import instances.constants as constants
from instances.config import DiagnosticToolsTest as diag_tools_test_conf


def run_in_container() -> None:
    client = docker.DockerClient(base_url=f'tcp://{diag_tools_test_conf.docker_base_url}')

    # build image
    image_info = client.images.build(
        path=diag_tools_test_conf.dockerfile_url,
        tag=diag_tools_test_conf.full_tag,
        pull=True,
        rm=True
    )
    image_id = image_info[0]['attrs']['Id']
    image_parent_id = image_info[0]['attrs']['Parent']

    # create mount directory
    mount_map = diag_tools_test_conf.mount_dir[0]
    [host_dir, container_dir] = mount_map.split(':')

    # copy script to that folder
    shutil.copy(
        constants.script_root,
        host_dir
    )

    # create container
    script_root = os.path.join(
        container_dir,
        os.path.basename(constants.script_root)
    )
    command = f'cd {script_root} && python3 test_diagnostic_tools.py run'
    container = client.containers.run(
        diag_tools_test_conf.full_tag,
        command=['/bin/bash', '-c', command],
        name=diag_tools_test_conf.test_name,
        remove=True,
        cap_add=diag_tools_test_conf.cap_add,
        security_opt=diag_tools_test_conf.security_opt,
        volumes=diag_tools_test_conf.mount_dir
    )

    # remove image
    client.images.remove(image_id)
    client.images.remove(image_parent_id)