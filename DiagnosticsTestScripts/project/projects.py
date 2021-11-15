'''In this module, we provide some function for creating and running dotnet projects.
'''

import os
import time
import shutil
import logging
from xml.etree import ElementTree as ET

import config
from utils import run_command_async, Popen, \
    run_command_sync


def create_publish_webapp(configuration: config.TestConfig, logger: logging.Logger):
    '''Create and publish a dotnet webapp

    '''
    logger.info('****** create publish webapp ******')
    project_dir = os.path.join(
        configuration.test_bed,
        'webapp'
    )
    rt_code = run_command_sync(
        f'dotnet new webapp -o {project_dir}',
        logger,
        cwd=configuration.test_bed,
    )
    if rt_code != 0:
        configuration.run_webapp = False
        logger.error('fail to create webapp!')
        logger.info('****** create publish webapp finished ******')
        return

    project_file = os.path.join(project_dir, 'webapp.csproj')

    tree = ET.parse(project_file)
    root = tree.getroot()
    if configuration.sdk_version[0] == '3':
        framework = 'netcoreapp' + configuration.sdk_version[:3]
    else:
        framework = 'net' + configuration.sdk_version[:3]
    root.find('PropertyGroup').find('TargetFramework').text = framework
    tree.write(project_file)

    if configuration.source_feed != '':
        rt_code = run_command_sync(
            f'dotnet build -o out -r {configuration.rid} --self-contained --source {configuration.source_feed}',
            logger,
            cwd=project_dir,
        )
        if rt_code == 0:
            logger.info('successfully create and build webapp.')
            logger.info('****** create publish webapp finished ******')
            return
    
    # if given runtime isn't available, try to publish without specifying rid.
    rt_code = run_command_sync(
        f'dotnet publish -o out -r {configuration.rid}',
        logger,
        cwd=project_dir
    )
    if rt_code != 0:
        rt_code = run_command_sync(
            f'dotnet publish -o out',
            logger,
            cwd=project_dir
        )

    if rt_code != 0:
        configuration.run_webapp = False
        logger.error('fail to publish webapp.')
    else:
        logger.info('successfully create and build webapp.')

    logger.info('****** create publish webapp finished ******')


def run_webapp(configuration, logger, project_dir: str) -> Popen:
    '''Start webapp and return the process instance.

    Args:
        project_dir: directory of webapp
    Return:
        webapp process instance
    '''
    tmp_path = os.path.join(project_dir, 'tmp')
    tmp_write = open(tmp_path, 'w+')
    tmp_read = open(tmp_path, 'r')
    if 'win' in configuration.rid:
        bin_extension = '.exe'
    else:
        bin_extension = ''

    if f'webapp{bin_extension}' in os.listdir(f'{project_dir}/out'):
        proc = run_command_async(
            f'{project_dir}/out/webapp{bin_extension}',
            logger,
            stdout=tmp_write
        )
    else:
        proc = run_command_async(
            f'dotnet {project_dir}/out/webapp.dll',
            logger,
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


def create_publish_consoleapp(configuration: config.TestConfig, logger: logging.Logger):
    '''Create and publish a dotnet console app.

    The console app is used to test startup feature of
        dotnet-counters/dotnet-trace.
    '''
    logger.info('****** create publish consoleapp ******')
    if int(configuration.sdk_version[0]) == 3:
        configuration.run_consoleapp = False
        logger.info(
            'ignore consoleapp: new feature isn\'t supported by .net core 3.1.'
        )
        logger.info('****** create publish consoleapp finished ******')
        return
    project_dir = os.path.join(
        configuration.test_bed,
        'consoleapp'
    )
    rt_code = run_command_sync(
        f'dotnet new console -o {project_dir}',
        logger,
        cwd=configuration.test_bed,
    )
    if rt_code != 0:
        configuration.run_consoleapp = False
        logger.error('fail to create console app!')
        logger.info('****** create publish consoleapp finished ******')
        return

    shutil.copy(
        os.path.join(configuration.work_dir, 'project', 'consoleapp_tmp'), 
        os.path.join(project_dir, 'Program.cs')
    )

    project_file = os.path.join(project_dir, 'consoleapp.csproj')

    tree = ET.parse(project_file)
    root = tree.getroot()
    if configuration.sdk_version[0] == '3':
        framework = 'netcoreapp' + configuration.sdk_version[:3]
    else:
        framework = 'net' + configuration.sdk_version[:3]
    root.find('PropertyGroup').find('TargetFramework').text = framework
    tree.write(project_file)

    if configuration.source_feed != '':
        rt_code = run_command_sync(
            f'dotnet build -o out -r {configuration.rid} --self-contained --source {configuration.source_feed}',
            logger,
            cwd=project_dir
        )
        if rt_code == 0:
            logger.info('successfully create and build console app.')
            logger.info('****** create publish consoleapp finished ******')
            return
        
    # if given runtime isn't available, try to publish without specifying rid.
    rt_code = run_command_sync(
        f'dotnet publish -o out -r {configuration.rid}',
        logger,
        cwd=project_dir
    )
    if rt_code != 0:
        rt_code = run_command_sync(
            f'dotnet publish -o out',
            logger,
            cwd=project_dir,
        )
    if rt_code != 0:
        configuration.run_consoleapp = False
        logger.error('fail to build console app!')
    else:
        logger.info('successfully create and build console app.')
    
    logger.info('****** create publish consoleapp finished ******')


def create_publish_GCDumpPlayground(configuration: config.TestConfig, logger: logging.Logger):
    '''Copy GCDumpPlayground to testbed then publish.

    '''
    logger.info('****** create publish GCDumpPlayground ******')
    template_project_dir = os.path.join(
        configuration.work_dir,
        'project',
        'GCDumpPlayground2'
    )
    project_dir = os.path.join(
        configuration.test_bed,
        'GCDumpPlayground2'
    )
    project_file = os.path.join(project_dir, 'GCDumpPlayground2.csproj')

    shutil.copytree(template_project_dir, project_dir)
    tree = ET.parse(project_file)
    root = tree.getroot()
    if configuration.sdk_version[0] == '3':
        framework = 'netcoreapp' + configuration.sdk_version[:3]
    else:
        framework = 'net' + configuration.sdk_version[:3]
    root.find('PropertyGroup').find('TargetFramework').text = framework
    tree.write(project_file)

    if configuration.source_feed != '':
        rt_code = run_command_sync(
            f'dotnet build -o out -r {configuration.rid} --self-contained --source {configuration.source_feed}',
            logger,
            cwd=project_dir
        )
        if rt_code == 0:
            logger.info('successfully create and build GCDumpPlayground.')
            logger.info('****** create publish GCDumpPlayground finished ******')
            return
    
    # if given runtime isn't available, try to publish without specifying rid.
    rt_code = run_command_sync(
        f'dotnet publish -o out -r {configuration.rid}',
        logger,
        cwd=project_dir,
    )
    if rt_code != 0:
        rt_code = run_command_sync(
            f'dotnet publish -o out',
            logger,
            cwd=project_dir,
        )
    if rt_code != 0:
        configuration.run_gcplayground = False
        logger.error('fail to build gcdumpplayground!')
    else:
        logger.info('successfully create and publish gcdumpplayground.')

    logger.info('****** create publish GCDumpPlayground finished ******')


def run_GCDumpPlayground(configuration: config.TestConfig, logger, project_dir: str)->Popen:
    '''Start GCDumpPlayground and return the process instance.

    Args:
        project_dir: directory of GCDumpPlayground
    Return:
        GCDumpPlayground process instance
    '''
    tmp_path = os.path.join(project_dir, 'tmp.txt')
    tmp_write = open(tmp_path, 'w+')

    if 'win' in configuration.rid:
        bin_extension = '.exe'
    else:
        bin_extension = ''

    if f'GCDumpPlayground2{bin_extension}' in os.listdir(f'{project_dir}/out'):
        proc = run_command_async(
            f'{project_dir}/out/GCDumpPlayground2{bin_extension} 0.1',
            logger,
            stdout=tmp_write
        )
    else:
        proc = run_command_async(
            f'dotnet {project_dir}/out/GCDumpPlayground2.dll 0.1',
            logger,
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
