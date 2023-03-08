import os
import shutil

from services.project.project import change_framework, build_project
from services.terminal import run_command_sync, PIPE
import instances.constants as constants
from instances.logger import ScriptLogger
from instances.project import oom


def create_build_oom(test_bed: str, 
                    dotnet_bin_path: str, 
                    env: dict, 
                    rid: str, 
                    sdk_version: str, 
                    logger: ScriptLogger):
    '''Copy project to testbed then publish.
    '''
    project_name = 'oom'
    logger.info(f'create {project_name}')
    template_project_dir = os.path.join(
        constants.script_root,
        'assets',
        project_name
    )
    oom.project_root = os.path.join(
        test_bed,
        f'{project_name}_net{sdk_version}_{rid}'
    )
    
    shutil.copytree(template_project_dir, oom.project_root)
    
    change_framework(oom.project_root, sdk_version)

    oom.runnable = build_project(oom.project_root, dotnet_bin_path, env, logger)

    oom.project_dll_path = os.path.join(oom.project_root, 'out', f'{project_name}.dll')
    

def run_oom(env: dict, cwd: str, sdk_version: str, rid: str, logger: ScriptLogger) -> str:
    '''Start project.

    Args:
        project_dir: directory of GCDumpPlayground
    '''
    env['COMPlus_DbgEnableMiniDump'] = '1'
    env['COMPlus_DbgMiniDumpType'] = '4'
    
    dump_path = os.path.join(
        cwd,
        (
            'dump_oom_'
            f'net{sdk_version}_'
            f'{rid}'
        )
    )
    env['COMPlus_DbgMiniDumpName'] = dump_path

    if 'win' in rid: ext = '.exe'
    else: ext = ''
    dotnet_bin_path = os.path.join(
        env['DOTNET_ROOT'],
        f'dotnet{ext}'
    )

    command = f'{dotnet_bin_path} {oom.project_dll_path}'
    outs, errs = run_command_sync(command, env=env, cwd=cwd, stdout=PIPE, stderr=PIPE)
    logger.info(f'run command:\n{command}\n{outs}\n{errs}')
    return dump_path
