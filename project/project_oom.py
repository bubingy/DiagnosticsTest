import os
import shutil

from CrossOSDACTest.config import TestConfig
from project.project import change_framework, build_project
from utils.terminal import Popen, run_command_sync
from utils.logger import ScriptLogger


def create_build_oom(conf: TestConfig, logger: ScriptLogger):
    '''Copy project to testbed then publish.
    '''
    logger.info(f'create oom')
    template_project_dir = os.path.join(
        conf.work_dir,
        'project',
        'oom'
    )
    project_dir = os.path.join(
        conf.test_bed,
        f'oom_net{conf.sdk_version}_{conf.rid}'
    )
    
    shutil.copytree(template_project_dir, project_dir)
    
    change_framework(project_dir, conf.sdk_version)

    build_project(project_dir, conf.dotnet, conf.rid, logger)
    

def run_oom(conf: TestConfig, logger: ScriptLogger) -> Popen:
    '''Start project.

    Args:
        project_dir: directory of GCDumpPlayground
    '''
    logger.info('run oom')
    project_dir = os.path.join(
        conf.test_bed,
        f'oom_net{conf.sdk_version}_{conf.rid}'
    )
    env = os.environ.copy()
    env['COMPlus_DbgEnableMiniDump'] = '1'
    dump_path = os.path.join(
        conf.dump_directory,
        (
            'dump_oom_'
            f'net{conf.sdk_version}_'
            f'{conf.rid}'
        )
    )
    env['COMPlus_DbgMiniDumpName'] = dump_path

    command = f'{conf.dotnet} {project_dir}/out/oom.dll'
    outs, errs = run_command_sync(command, env=env)
    logger.info(f'run command:\n{command}\n{outs}\n{errs}')
    if not os.path.exists(dump_path):
        logger.error(f'fail to generate dump!')
    logger.info(f'generate dump finished')
    return dump_path
