import os
import shutil

from services.project.project import change_framework, build_project
from services.terminal import run_command_sync, PIPE
import instances.constants as constants
from instances.logger import ScriptLogger
from instances.project import uhe


def create_build_uhe(test_bed: str, 
                    dotnet_bin_path: str, 
                    env: dict, 
                    rid: str, 
                    sdk_version: str, 
                    logger: ScriptLogger):
    '''Copy project to testbed then publish.
    '''
    project_name = 'uhe'
    logger.info(f'create uhe')
    template_project_dir = os.path.join(
        constants.script_root,
        'assets',
        project_name
    )
    uhe.project_root = os.path.join(
        test_bed,
        f'uhe_net{sdk_version}_{rid}'
    )
    
    shutil.copytree(template_project_dir, uhe.project_root)
    
    change_framework(uhe.project_root, sdk_version)

    uhe.runnable = build_project(uhe.project_root, dotnet_bin_path, env, logger)

    ext = os.path.splitext(dotnet_bin_path)[-1]
    uhe.project_bin_path = os.path.join(uhe.project_root, 'out', f'{project_name}{ext}')
    

def run_uhe(env: dict, cwd: str, sdk_version: str, rid: str, logger: ScriptLogger) -> str:
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

    outs, errs = run_command_sync(uhe.project_bin_path, env=env, cwd=cwd, stdout=PIPE, stderr=PIPE)
    logger.info(f'run command:\n{uhe.project_bin_path}\n{outs}\n{errs}')
    return dump_path
