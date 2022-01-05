'''In this module, we provide some function for creating and running dotnet projects.
'''

import os
import shutil
from xml.etree import ElementTree as ET

from config import TestConfig
from utils import run_command_sync, run_command_async


def create_publish_project(conf: TestConfig, project_name: str):
    '''Copy project to testbed then publish.
    '''
    template_project_dir = os.path.join(
        conf.work_dir,
        'Projects',
        project_name
    )
    project_dir = os.path.join(
        conf.test_bed,
        f'{project_name}-net{conf.sdk_version}'
    )
    project_file = os.path.join(project_dir, f'{project_name}.csproj')
    print(f'****** create gcperfsim ******')
    try:
        shutil.copytree(template_project_dir, project_dir)
        tree = ET.parse(project_file)
        root = tree.getroot()
        if conf.sdk_version[0] == '3':
            framework = 'netcoreapp' + conf.sdk_version[:3]
        else:
            framework = 'net' + conf.sdk_version[:3]
        root.find('PropertyGroup').find('TargetFramework').text = framework
        tree.write(project_file)
    except Exception as e:
        print(f'fail to create gcperfsim: {e}')
        return

    rt_code_publish = run_command_sync(
        'dotnet publish -o out',
        cwd=project_dir
    )
    if rt_code_publish == 0:
        print(f'publish gcperfsim successfully')
    else:
        print(f'fail to publish gcperfsim')


def run_project(conf: TestConfig, project_name: str):
    '''Start project.

    Args:
        project_dir: directory of GCDumpPlayground
    '''
    project_dir = os.path.join(
        conf.test_bed,
        f'{project_name}-net{conf.sdk_version}'
    )
    env = os.environ.copy()
    env['COMPlus_PerfMapEnabled'] = '1'
    env['COMPlus_EnableEventLog'] = '1'

    proc = run_command_async(
        f'dotnet {project_dir}/out/{project_name}.dll',
        env=env
    )
    return proc


def collect_trace(conf: TestConfig, duration: int=30):
    trace_path = os.path.join(
        conf.trace_directory,
        f'trace_net{conf.sdk_version}_{conf.rid}'
    )
    env = os.environ.copy()
    env['COMPlus_PerfMapEnabled'] = '1'
    env['COMPlus_EnableEventLog'] = '1'

    run_command_sync(
        f'/bin/bash {conf.test_bed}/perfcollect collect {trace_path} -collectsec {duration}',
        env=env
    )