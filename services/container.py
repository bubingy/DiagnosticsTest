import os
import shutil

import instances.constants as constants


def extract_id(full_id: str):
    return full_id.split(':')[1]


def run_in_container(docker_base_url: str,
                     dockerfile_url: str,
                     full_tag: str,
                     mount_dir: list,
                     test_name: str,
                     cap_add: list,
                     security_opt: list,
                     run_command: str) -> None:
    import docker
    client = docker.DockerClient(base_url=f'tcp://{docker_base_url}')

    # build image
    # image_id = None
    # image_parent_id = None
    # try:
    #     print('building image')
    #     image_info = client.images.build(
    #         path=dockerfile_url,
    #         tag=full_tag,
    #         pull=True,
    #         rm=True
    #     )
    #     image_id = extract_id(image_info[0].attrs['Id'])
    #     image_parent_id = extract_id(image_info[0].attrs['Parent'])
    # except Exception as e:
    #     print(f'fail to build image: {e}')

    
    try:
        # create mount directory
        mount_map = mount_dir[0]
        [host_dir, container_dir] = mount_map.split(':')
        if not os.path.exists(host_dir): os.makedirs(host_dir)

        # copy script to that folder
        shutil.copytree(
            constants.script_root,
            os.path.join(host_dir, os.path.basename(constants.script_root))
        )
    except Exception as e:
        print(f'fail to create mount directory or copy script to container: {e}')
        # client.images.remove(image_id)
        # client.images.remove(image_parent_id)

    # create container
    print('run container')
    script_root = os.path.join(
        container_dir,
        os.path.basename(constants.script_root)
    )
    command = f'cd {script_root} && {run_command}'

    try:
        container = client.containers.run(
            full_tag,
            command=['/bin/bash', '-c', command],
            name=test_name,
            remove=True,
            cap_add=cap_add,
            security_opt=security_opt,
            volumes=mount_dir
        )
    except Exception as e:
        print(f'fail to create and run container: {e}')
    # finally:
    #     # remove image
    #     client.images.remove(image_id)
    #     client.images.remove(image_parent_id)