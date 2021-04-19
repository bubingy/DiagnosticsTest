'''In this module, we provide some function for creating and running dotnet projects.
'''

import os
import shutil
from xml.etree import ElementTree as ET

from config import configuration
from utils import run_command_sync, Result


log_path = os.path.join(configuration.test_bed, 'projects.log')


def create_publish_project(project_name: str)->Result:
    '''Copy project to testbed then publish.

    Return:
        return Result class
    '''
    template_project_dir = os.path.join(
        configuration.work_dir,
        'Projects',
        project_name
    )
    project_dir = os.path.join(
        configuration.test_bed,
        project_name
    )
    project_file = os.path.join(project_dir, f'{project_name}.csproj')
    try:
        shutil.copytree(template_project_dir, project_dir)
        tree = ET.parse(project_file)
        root = tree.getroot()
        if configuration.sdk_version[0] == '3':
            framework = 'netcoreapp' + configuration.sdk_version[:3]
        else:
            framework = 'net' + configuration.sdk_version[:3]
        root.find('PropertyGroup').find('TargetFramework').text = framework
        tree.write(project_file)
    except Exception as exception:
        return Result(
            -1, 
            f'fail to copy f{project_name} to {configuration.test_bed}', 
            exception
        )
    rt_code_publish = run_command_sync(
        'dotnet publish -o out',
        cwd=project_dir,
        log_path=log_path
    )
    if rt_code_publish == 0:
        return Result(0, f'successfully publish {project_name}', project_dir)
    else:
        return Result(
            rt_code_publish,
            f'fail to publish {project_name}',
            None
        )


def run_project(project_name: str):
    '''Start project.

    Args:
        project_dir: directory of GCDumpPlayground
    '''
    project_dir = os.path.join(
        configuration.test_bed,
        project_name
    )
    env = os.environ.copy()
    env['COMPlus_DbgEnableMiniDump'] = '1'
    dump_path = os.path.join(
        configuration.dump_directory,
        (
            'dump_'
            f'net{configuration.sdk_version[0]}{configuration.sdk_version[2]}_'
            f'{configuration.rid}_{project_name}'
        )
    )
    env['COMPlus_DbgMiniDumpName'] = dump_path

    run_command_sync(
        f'{project_dir}/out/{project_name}',
        env=env
    )
    return dump_path
