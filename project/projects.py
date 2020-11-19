'''In this module, we provide some function for creating and running dotnet projects.
'''

import os
import time
import shutil
from xml.etree import ElementTree as ET

from config import configuration
from utils import run_command_async, Popen, \
    run_command_sync, Result, PIPE


def create_publish_webapp()->Result:
    '''Create and publish a dotnet webapp

    Return:
        return Result class
    '''
    webapp_dir = os.path.join(
        configuration.test_bed,
        'webapp'
    )
    rt_code_create = run_command_sync(
        f'dotnet new webapp -o {webapp_dir}',
        cwd=configuration.test_bed
    )
    rt_code_publish = run_command_sync(
        f'dotnet publish -o out',
        cwd=webapp_dir
    )
    if rt_code_publish == 0 and rt_code_create == 0:
        return Result(0, 'successfully create webapp', webapp_dir)
    else:
        return Result(
            -1, 
            'fail to create webapp', 
            {
                'create': rt_code_create,
                'publish': rt_code_publish
            }
        )


def run_webapp(project_dir: str)->Popen:
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
        proc = run_command_async(
            f'{project_dir}/out/webapp.exe', 
            stdout=tmp_write
        )
    else:
        proc = run_command_async(
            f'{project_dir}/out/webapp', 
            cwd=f'{project_dir}/out',  
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


def create_publish_consoleapp()->Result:
    '''Create and publish a dotnet console app.

    The console app is used to test startup feature of 
        dotnet-counters/dotnet-trace.

    Return:
        return Result class
    '''
    consoleapp_dir = os.path.join(
        configuration.test_bed,
        'consoleapp'
    )
    rt_code_create = run_command_sync(
        f'dotnet new console -o {consoleapp_dir}',
        cwd=configuration.test_bed
    )
    shutil.copy(
        os.path.join(configuration.tool_root, 'project', 'consoleapp_tmp'), 
        os.path.join(consoleapp_dir, 'Program.cs')
    )
    rt_code_publish = run_command_sync(
        f'dotnet publish -o out',
        cwd=consoleapp_dir
    )

    if rt_code_publish == 0 and rt_code_create == 0:
        return Result(0, 'successfully create console app', consoleapp_dir)
    else:
        return Result(
            -1, 
            'fail to create console app', 
            {
                'create': rt_code_create,
                'publish': rt_code_publish
            }
        )


def create_publish_GCDumpPlayground()->Result:
    '''Copy GCDumpPlayground to testbed then publish.

    Return:
        return Result class
    '''
    template_project_dir = os.path.join(
        configuration.tool_root,
        'project',
        'GCDumpPlayground2'
    )
    project_dir = os.path.join(
        configuration.test_bed, 
        'GCDumpPlayground2'
    )
    project_file = os.path.join(project_dir, 'GCDumpPlayground2.csproj')
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
    except Exception as e:
        return Result(-1, 'fail to copy GCDumpPlayground to testbed', e)
    rt_code_publish = run_command_sync(
        f'dotnet publish -o out',
        cwd=project_dir
    )
    if rt_code_publish == 0:
        return Result(0, 'successfully publish GCDumpPlayground', project_dir)
    else:
        return Result(
            rt_code_publish, 
            'fail to publish GCDumpPlayground', 
            None
        )
    

def run_GCDumpPlayground(project_dir: str)->Popen:
    '''Start GCDumpPlayground and return the process instance.

    Args:
        project_dir: directory of GCDumpPlayground
    Return:
        GCDumpPlayground process instance
    '''
    extend_name = ''
    if 'win' in configuration.rid:
        extend_name = '.exe'
    tmp_path = os.path.join(project_dir, 'tmp.txt')
    tmp_writer = open(tmp_path, 'w+')

    proc = run_command_async(
        f'{project_dir}/out/GCDumpPlayground2{extend_name} 0.1',
        stdout=tmp_writer
    )
        
    while True:
        with open(tmp_path, 'r+') as f:
            if 'Pause for gcdumps.' in f.read():
                print('GCDumpPlayground2 is running!')
                break
            else:
                time.sleep(2)
    tmp_writer.close()
    return proc