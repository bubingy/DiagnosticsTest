import os
import time

from DiagnosticsToolsTest import config
from project.project import create_project, change_framework, build_project
from utils.logger import ScriptLogger
from utils.terminal import run_command_async, Popen


def create_build_webapp(configuration: config.TestConfig, logger: ScriptLogger):
    '''Create and publish a dotnet webapp

    '''
    project_dir = os.path.join(configuration.test_bed, 'webapp')
    configuration.run_webapp = create_project('webapp', project_dir, configuration.dotnet, logger)
    change_framework(project_dir, configuration.sdk_version)
    configuration.run_webapp = build_project(project_dir, configuration.dotnet, configuration.rid, logger)


def run_webapp(configuration: config.TestConfig, project_dir: str) -> Popen:
    '''Start webapp and return the process instance.

    Args:
        project_dir: directory of webapp
    Return:
        webapp process instance
    '''
    tmp_path = os.path.join(project_dir, 'tmp')
    tmp_write = open(tmp_path, 'w+')
    tmp_read = open(tmp_path, 'r')
    if 'win' in configuration.rid:
        bin_extension = '.exe'
    else:
        bin_extension = ''

    if f'webapp{bin_extension}' in os.listdir(f'{project_dir}/out'):
        proc = run_command_async(
            f'{project_dir}/out/webapp{bin_extension}',
            stdout=tmp_write
        )
    else:
        proc = run_command_async(
            f'{configuration.dotnet} {project_dir}/out/webapp.dll',
            stdout=tmp_write
        )
        
    while True:
        if 'Application started' in tmp_read.read():
            print('webapp is running!')
            tmp_read.close()
            break
        else:
            time.sleep(2)
    tmp_write.close()
    return proc