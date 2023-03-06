import os
import time
from subprocess import Popen

from services.project.project import create_project, change_framework, build_project
from services.terminal import run_command_async
from instances.logger import ScriptLogger
from instances.project import webapp


def create_build_webapp(test_bed: str, dotnet_bin_path: str, sdk_version: str, env: dict, logger: ScriptLogger):
    '''Create and publish a dotnet webapp

    '''
    project_name = 'webapp'
    webapp.project_root = os.path.join(
        test_bed,
        f'webapp-net{sdk_version}'
    )
    webapp.runnable = create_project(
        project_name,
        'webapp', 
        webapp.project_root, 
        dotnet_bin_path, 
        env,
        logger
    )
    change_framework(webapp.project_root, sdk_version)
    webapp.runnable = webapp.runnable and build_project(
        webapp.project_root,
        dotnet_bin_path, 
        env, 
        logger
    )

    ext = os.path.splitext(dotnet_bin_path)[-1]
    webapp.project_bin_path = os.path.join(webapp.project_root, 'out', f'{project_name}{ext}')
    logger.info(f'create webapp finished')


def run_webapp(env: dict, cwd: str) -> Popen:
    '''Start webapp and return the process instance.

    Args:
        project_dir: directory of webapp
    Return:
        webapp process instance
    '''
    tmp_path = os.path.join(webapp.project_root, 'tmp')
    tmp_write = open(tmp_path, 'w+')
    tmp_read = open(tmp_path, 'r')

    proc = run_command_async(
        webapp.project_bin_path,
        stdout=tmp_write,
        env=env,
        cwd=cwd
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