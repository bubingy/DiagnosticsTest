import os
import time
import shutil
from subprocess import Popen

from services.project.project import change_framework, build_project
from services.terminal import run_command_async
import instances.constants as constants
from instances.logger import ScriptLogger
from instances.project import gcdumpapp


def create_build_GCDumpPlayground(test_bed: str,
                                dotnet_bin_path: str,
                                sdk_version: str,
                                env: dict,
                                logger: ScriptLogger):
    '''Copy GCDumpPlayground to testbed then publish.

    '''
    project_name = 'GCDumpPlayground2'
    logger.info('create GCDumpPlayground')
    template_project_dir = os.path.join(
        constants.script_root,
        'assets',
        project_name
    )
    gcdumpapp.project_root = os.path.join(
        test_bed,
        f'GCDumpPlayground2-net{sdk_version}'
    )

    shutil.copytree(template_project_dir, gcdumpapp.project_root)

    change_framework(gcdumpapp.project_root, sdk_version)

    gcdumpapp.runnable = build_project(
        gcdumpapp.project_root,
        dotnet_bin_path,
        env,
        logger
    )

    ext = os.path.splitext(dotnet_bin_path)[-1]
    gcdumpapp.project_bin_path = os.path.join(gcdumpapp.project_root, 'out', f'{project_name}{ext}')


def run_GCDumpPlayground(env: dict, cwd: str) -> Popen:
    '''Start GCDumpPlayground and return the process instance.

    Args:
        project_dir: directory of GCDumpPlayground
    Return:
        GCDumpPlayground process instance
    '''
    tmp_path = os.path.join(gcdumpapp.project_root, 'tmp.txt')
    tmp_write = open(tmp_path, 'w+')

    proc = run_command_async(
        f'{gcdumpapp.project_bin_path} 0.05',
        stdout=tmp_write,
        env=env,
        cwd=cwd
    )

    while True:
        with open(tmp_path, 'r+') as f:
            if 'Pause for gcdumps.' in f.read():
                print('GCDumpPlayground2 is running!')
                break
            else:
                time.sleep(2)
    tmp_write.close()
    return proc
