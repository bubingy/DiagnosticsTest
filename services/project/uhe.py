import os
import shutil

from services.project.project import change_framework, build_project
from services.terminal import run_command_sync
import types.constants as constants
from types.logger import ScriptLogger
from types.project import uhe


def create_build_uhe(test_bed: str, 
                    dotnet_bin_path: str, 
                    env: dict, 
                    rid: str, 
                    sdk_version: str, 
                    logger: ScriptLogger):
    '''Copy project to testbed then publish.
    '''
    logger.info(f'create uhe')
    template_project_dir = os.path.join(
        constants.script_root,
        'assets',
        'uhe'
    )
    uhe.project_root = os.path.join(
        test_bed,
        f'uhe_net{sdk_version}_{rid}'
    )
    
    shutil.copytree(template_project_dir, uhe.project_root)
    
    change_framework(uhe.project_root, sdk_version)

    uhe.runnable = build_project(uhe.project_root, dotnet_bin_path, env, logger)

    ext = os.path.splitext(dotnet_bin_path)[-1]
    uhe.project_bin_path = os.path.join(uhe.project_root, 'out', f'uhe{ext}')
    

def run_uhe(env: dict, cwd: str, sdk_version: str, rid: str) -> str:
    '''Start project.

    Args:
        project_dir: directory of GCDumpPlayground
    '''
    env['COMPlus_DbgEnableMiniDump'] = '1'
    env['COMPlus_DbgMiniDumpType'] = '4'
    
    dump_path = os.path.join(
        cwd,
        (
            'dump_uhe_'
            f'net{sdk_version}_'
            f'{rid}'
        )
    )
    env['COMPlus_DbgMiniDumpName'] = dump_path

    run_command_sync(uhe.project_bin_path, env=env, cwd=cwd)
    
    return dump_path
