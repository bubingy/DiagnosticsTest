import os
import time
import shutil

from DiagnosticsToolsTest import config
from project.project import change_framework, build_project
from utils.terminal import Popen, run_command_async
from utils.logger import ScriptLogger


def create_build_GCDumpPlayground(configuration: config.TestConfig, logger: ScriptLogger):
    '''Copy GCDumpPlayground to testbed then publish.

    '''
    logger.info('create GCDumpPlayground')
    template_project_dir = os.path.join(
        configuration.work_dir,
        'project',
        'GCDumpPlayground2'
    )
    project_dir = os.path.join(
        configuration.test_bed,
        'GCDumpPlayground2'
    )

    shutil.copytree(template_project_dir, project_dir)

    change_framework(project_dir, configuration.sdk_version)

    configuration.run_gcplayground = build_project(project_dir, configuration.dotnet, configuration.rid, logger)


def run_GCDumpPlayground(configuration: config.TestConfig,   project_dir: str)->Popen:
    '''Start GCDumpPlayground and return the process instance.

    Args:
        project_dir: directory of GCDumpPlayground
    Return:
        GCDumpPlayground process instance
    '''
    tmp_path = os.path.join(project_dir, 'tmp.txt')
    tmp_write = open(tmp_path, 'w+')

    if 'win' in configuration.rid:
        bin_extension = '.exe'
    else:
        bin_extension = ''

    if f'GCDumpPlayground2{bin_extension}' in os.listdir(f'{project_dir}/out'):
        proc = run_command_async(
            f'{project_dir}/out/GCDumpPlayground2{bin_extension} 0.05',
            stdout=tmp_write
        )
    else:
        proc = run_command_async(
            f'{configuration.dotnet} {project_dir}/out/GCDumpPlayground2.dll 0.05', 
            stdout=tmp_write
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
