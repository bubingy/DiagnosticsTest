import os
import shutil

from CrossOSDACTest.config import TestConfig
from project.project import change_framework, build_project
from utils.terminal import Popen, run_command_sync
from utils.logger import ScriptLogger


def create_build_uhe(conf: TestConfig, logger: ScriptLogger):
    '''Copy project to testbed then publish.
    '''
    logger.info(f'create uhe')
    template_project_dir = os.path.join(
        conf.work_dir,
        'project',
        'uhe'
    )
    project_dir = os.path.join(
        conf.test_bed,
        f'uhe'
    )
    
    shutil.copytree(template_project_dir, project_dir)
    
    change_framework(project_dir, conf.sdk_version)

    build_project(project_dir, conf.dotnet, conf.rid, logger)
    

def run_uhe(conf: TestConfig, logger: ScriptLogger) -> Popen:
    '''Start project.

    Args:
        project_dir: directory of GCDumpPlayground
    '''
    logger.info('run uhe')
    project_dir = os.path.join(
        conf.test_bed,
        f'uhe'
    )
    env = os.environ.copy()
    env['COMPlus_DbgEnableMiniDump'] = '1'
    dump_path = os.path.join(
        conf.dump_directory,
        (
            'dump_uhe_'
            f'net{conf.sdk_version}_'
            f'{conf.rid}'
        )
    )
    env['COMPlus_DbgMiniDumpName'] = dump_path

    command = f'{conf.dotnet} {project_dir}/out/uhe.dll'
    outs, errs = run_command_sync(command, env=env)
    logger.info(f'run command:\n{command}\n{outs}\n{errs}')
    if not os.path.exists(dump_path):
        logger.error(f'fail to generate dump!')
    logger.info(f'generate dump finished')
    return dump_path
