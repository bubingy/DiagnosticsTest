'''In this module, we provide some function for creating and running dotnet projects.
'''

import os
import time
import shutil
from xml.etree import ElementTree as ET

import config
from utils import run_command_async, Popen, \
    run_command_sync, Result, test_logger


@test_logger(os.path.join(config.configuration.test_result, f'{__name__}.log'))
def create_publish_webapp(log_path: os.PathLike=None) -> Result:
    '''Create and publish a dotnet webapp

    Return:
        return Result class
    '''
    project_dir = os.path.join(
        config.configuration.test_bed,
        'webapp'
    )
    rt_code = run_command_sync(
        f'dotnet new webapp -o {project_dir}',
        cwd=config.configuration.test_bed,
        log_path=log_path
    )
    if rt_code != 0:
        config.configuration.run_webapp = False
        return Result(-1, 'fail to create webapp.', None)

    if config.configuration.source_feed != '':
        rt_code = run_command_sync(
            f'dotnet build -o out -r {config.configuration.rid} --self-contained --source {config.configuration.source_feed}',
            cwd=project_dir,
            log_path=log_path
        )
        if rt_code == 0:
            return Result(0, 'successfully create and publish webapp.', project_dir)
    
    # if given runtime isn't available, try to publish without specifying rid.
    rt_code = run_command_sync(
        f'dotnet publish -o out -r {config.configuration.rid}',
        cwd=project_dir,
        log_path=log_path
    )
    if rt_code != 0:
        rt_code = run_command_sync(
            f'dotnet publish -o out',
            cwd=project_dir,
            log_path=log_path
        )

    if rt_code != 0:
        config.configuration.run_webapp = False
        return Result(-1, 'fail to publish webapp.', None)
    else:
        return Result(0, 'successfully create and publish webapp.', project_dir)


def run_webapp(project_dir: str) -> Popen:
    '''Start webapp and return the process instance.

    Args:
        project_dir: directory of webapp
    Return:
        webapp process instance
    '''
    tmp_path = os.path.join(project_dir, 'tmp')
    tmp_write = open(tmp_path, 'w+')
    tmp_read = open(tmp_path, 'r')
    if 'win' in config.configuration.rid:
        bin_extension = '.exe'
    else:
        bin_extension = ''

    if f'webapp{bin_extension}' in os.listdir(f'{project_dir}/out'):
        proc = run_command_async(
            f'{project_dir}/out/webapp{bin_extension}',
            stdout=tmp_write
        )
    else:
        proc = run_command_async(
            f'dotnet {project_dir}/out/webapp.dll',
            stdout=tmp_write
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


@test_logger(os.path.join(config.configuration.test_result, f'{__name__}.log'))
def create_publish_consoleapp(log_path: os.PathLike=None) -> Result:
    '''Create and publish a dotnet console app.

    The console app is used to test startup feature of
        dotnet-counters/dotnet-trace.

    Return:
        return Result class
    '''
    if int(config.configuration.sdk_version[0]) == 3:
        with open(log_path, 'a+') as f:
            f.write(f'won\'t create and publish consoleapp: new feature isn\'t supported by .net core 3.\n')
        config.configuration.run_consoleapp = False
        return Result(-1, 'not supported sdk.', None)
    project_dir = os.path.join(
        config.configuration.test_bed,
        'consoleapp'
    )
    rt_code = run_command_sync(
        f'dotnet new console -o {project_dir}',
        cwd=config.configuration.test_bed,
        log_path=log_path
    )
    if rt_code != 0:
        config.configuration.run_consoleapp = False
        return Result(-1, 'fail to create consoleapp.', None)
    shutil.copy(
        os.path.join(config.configuration.work_dir, 'project', 'consoleapp_tmp'), 
        os.path.join(project_dir, 'Program.cs')
    )

    if config.configuration.source_feed != '':
        rt_code = run_command_sync(
            f'dotnet build -o out -r {config.configuration.rid} --self-contained --source {config.configuration.source_feed}',
            cwd=project_dir,
            log_path=log_path
        )
        if rt_code == 0:
            return Result(0, 'successfully create and publish consoleapp.', project_dir)
        
    # if given runtime isn't available, try to publish without specifying rid.
    rt_code = run_command_sync(
        f'dotnet publish -o out -r {config.configuration.rid}',
        cwd=project_dir,
        log_path=log_path
    )
    if rt_code != 0:
        rt_code = run_command_sync(
            f'dotnet publish -o out',
            cwd=project_dir,
            log_path=log_path
        )
    if rt_code != 0:
        config.configuration.run_consoleapp = False
        return Result(-1, 'fail to publish consoleapp.', None)
    else:
        return Result(0, 'successfully create and publish consoleapp', project_dir)


@test_logger(os.path.join(config.configuration.test_result, f'{__name__}.log'))
def create_publish_GCDumpPlayground(log_path: os.PathLike=None) -> Result:
    '''Copy GCDumpPlayground to testbed then publish.

    Return:
        return Result class
    '''
    template_project_dir = os.path.join(
        config.configuration.work_dir,
        'project',
        'GCDumpPlayground2'
    )
    project_dir = os.path.join(
        config.configuration.test_bed,
        'GCDumpPlayground2'
    )
    project_file = os.path.join(project_dir, 'GCDumpPlayground2.csproj')
    try:
        shutil.copytree(template_project_dir, project_dir)
        tree = ET.parse(project_file)
        root = tree.getroot()
        if config.configuration.sdk_version[0] == '3':
            framework = 'netcoreapp' + config.configuration.sdk_version[:3]
        else:
            framework = 'net' + config.configuration.sdk_version[:3]
        root.find('PropertyGroup').find('TargetFramework').text = framework
        tree.write(project_file)
    except Exception as exception:
        config.configuration.run_gcplayground = False
        return Result(-1, 'fail to copy GCDumpPlayground to testbed', exception)

    if config.configuration.source_feed != '':
        rt_code = run_command_sync(
            f'dotnet build -o out -r {config.configuration.rid} --self-contained --source {config.configuration.source_feed}',
            cwd=project_dir,
            log_path=log_path
        )
        if rt_code == 0:
            return Result(0, 'successfully create and publish GCDumpPlayground.', project_dir)
    
    # if given runtime isn't available, try to publish without specifying rid.
    rt_code = run_command_sync(
        f'dotnet publish -o out -r {config.configuration.rid}',
        cwd=project_dir,
        log_path=log_path
    )
    if rt_code != 0:
        rt_code = run_command_sync(
            f'dotnet publish -o out',
            cwd=project_dir,
            log_path=log_path
        )
    if rt_code != 0:
        config.configuration.run_gcplayground = False
        return Result(-1, 'fail to publish gcdumpplayground.', None)
    else:
        return Result(0, 'successfully create and publish gcdumpplayground.', project_dir)


def run_GCDumpPlayground(project_dir: str)->Popen:
    '''Start GCDumpPlayground and return the process instance.

    Args:
        project_dir: directory of GCDumpPlayground
    Return:
        GCDumpPlayground process instance
    '''
    tmp_path = os.path.join(project_dir, 'tmp.txt')
    tmp_write = open(tmp_path, 'w+')

    if 'win' in config.configuration.rid:
        bin_extension = '.exe'
    else:
        bin_extension = ''

    if f'GCDumpPlayground2{bin_extension}' in os.listdir(f'{project_dir}/out'):
        proc = run_command_async(
            f'{project_dir}/out/GCDumpPlayground2{bin_extension} 0.1',
            stdout=tmp_write
        )
    else:
        proc = run_command_async(
            f'dotnet {project_dir}/out/GCDumpPlayground2.dll 0.1',
            stdout=tmp_write
        )

    while True:
        with open(tmp_path, 'r+') as f:
            if 'Pause for gcdumps.' in f.read():
                print('GCDumpPlayground2 is running!')
                break
            else:
                time.sleep(2)
    tmp_write.close()
    return proc
