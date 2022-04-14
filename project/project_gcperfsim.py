import os
import shutil

from LTTngTest.config import TestConfig
from project.project import change_framework, build_project
from utils.terminal import Popen, run_command_sync, run_command_async
from utils.logger import ScriptLogger


def create_build_gcperfsim(conf: TestConfig, logger: ScriptLogger):
    '''Copy project to testbed then publish.
    '''
    logger.info(f'create gcperfsim')
    template_project_dir = os.path.join(
        conf.work_dir,
        'project',
        'gcperfsim'
    )
    project_dir = os.path.join(
        conf.test_bed,
        f'gcperfsim'
    )
    
    shutil.copytree(template_project_dir, project_dir)
    
    change_framework(project_dir, conf.sdk_version)

    build_project(project_dir, conf.dotnet, conf.rid, logger)
    

def run_gcperfsim(conf: TestConfig) -> Popen:
    '''Start project.

    Args:
        project_dir: directory of GCDumpPlayground
    '''
    project_dir = os.path.join(
        conf.test_bed,
        f'gcperfsim'
    )
    env = os.environ.copy()
    env['COMPlus_PerfMapEnabled'] = '1'
    env['COMPlus_EnableEventLog'] = '1'

    proc = run_command_async(
        f'{project_dir}/out/gcperfsim',
        env=env
    )
    return proc


def collect_trace(conf: TestConfig, logger: ScriptLogger, duration: int=30):
    logger.info(f'start collect trace')
    trace_path = os.path.join(
        conf.trace_directory,
        f'trace_net{conf.sdk_version}_{conf.rid}'
    )
    env = os.environ.copy()
    env['COMPlus_PerfMapEnabled'] = '1'
    env['COMPlus_EnableEventLog'] = '1'
    command = f'/bin/bash {conf.test_bed}/perfcollect collect {trace_path} -collectsec {duration}'
    outs, errs = run_command_sync(command, env=env)
    logger.info(f'run command:\n{command}\n{outs}')
    if errs != '':
        logger.error(f'fail to collect trace!\n{errs}')
    logger.info(f'collection finished')