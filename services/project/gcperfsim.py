import os
import shutil
from subprocess import Popen

from services.project.project import change_framework, build_project
from services.terminal import run_command_async
import instances.constants as constants
from instances.logger import ScriptLogger
from instances.project import gcperfsim


def create_build_gcperfsim(test_bed: str, dotnet_bin_path: str, env: dict, sdk_version: str, logger: ScriptLogger):
    '''Copy project to testbed then publish.
    '''
    logger.info(f'create gcperfsim')
    template_project_dir = os.path.join(
        constants.script_root,
        'assets',
        'gcperfsim'
    )
    gcperfsim.project_root = os.path.join(
        test_bed,
        'gcperfsim'
    )
    
    shutil.copytree(template_project_dir, gcperfsim.project_root)
    
    change_framework(gcperfsim.project_root, sdk_version)

    gcperfsim.runnable = build_project(
        gcperfsim.project_root,
        dotnet_bin_path,
        env,
        logger
    )
    
    ext = os.path.splitext(dotnet_bin_path)[-1]
    gcperfsim.project_bin_path = os.path.join(gcperfsim.project_root, 'out', f'gcperfsim{ext}')


def run_gcperfsim(env: dict, cwd: str) -> Popen:
    '''Start project.

    Args:
        project_dir: directory of GCDumpPlayground
    '''
    env['COMPlus_PerfMapEnabled'] = '1'
    env['COMPlus_EnableEventLog'] = '1'

    proc = run_command_async(
        gcperfsim.project_bin_path,
        env=env,
        cwd=cwd
    )
    return proc
