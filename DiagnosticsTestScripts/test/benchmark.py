# coding=utf-8

import os
import shutil
from xml.etree import ElementTree as ET

import config
from utils import run_command_sync, test_logger


@test_logger(os.path.join(config.configuration.test_result, f'{__name__}.log'))
def download_diagnostics(log_path: os.PathLike=None):
    '''Clone diagnostics from github
    '''
    if config.configuration.run_benchmarks is False:
        message = 'ignore benchmarks, so the repo won\'t be downloaded.\n'
        print(message)
        with open(log_path, 'a+') as log:
            log.write(message)
        return
    rt_code = run_command_sync(
        'git clone https://github.com/dotnet/diagnostics.git',
        log_path=log_path,
        cwd=config.configuration.test_bed
    )
    if rt_code != 0:
        message = 'fail to download diagnostics!\n'
        print(message)
        with open(log_path, 'a+') as log:
            log.write(message)
        return

    repo_dir = os.path.join(
        config.configuration.test_bed, 'diagnostics'
    )
    rt_code = run_command_sync(
        f'git reset --hard {config.configuration.tool_commit}',
        log_path=log_path,
        cwd=repo_dir
    )
    if rt_code != 0:
        message = 'fail to reset commit id!\n'
        print(message)
        with open(log_path, 'a+') as log:
            log.write(message)
        return

    project_dir = os.path.join(
        repo_dir, 'src', 'tests', 'benchmarks'
    )
    project_file = os.path.join(project_dir, 'benchmarks.csproj')
    try:
        tree = ET.parse(project_file)
        root = tree.getroot()
        root.find('PropertyGroup').find('TargetFramework').text = \
            f'netcoreapp{config.configuration.sdk_version[:3]}'
        tree.write(project_file)
        message = 'successfully config benchmark.\n'
    except Exception as e:
        message = f'fail to config benchmark: {e}.\n'

    print(message)
    with open(log_path, 'a+') as log:
        log.write(message)
    

@test_logger(os.path.join(config.configuration.test_result, f'{__name__}.log'))
def run_benchmark(log_path: os.PathLike=None):
    '''Run benchmark

    '''
    if config.configuration.run_benchmarks is False:
        message = 'ignore benchmarks.\n'
        print(message)
        with open(log_path, 'a+') as log:
            log.write(message)
        return
    project_dir = os.path.join(
        config.configuration.test_bed, 'diagnostics', 
        'src', 'tests', 'benchmarks'
    )
    try:
        rt_code = run_command_sync(
            'dotnet run -c release',
            log_path=log_path,
            cwd=project_dir
        )
        shutil.copytree(
            os.path.join(project_dir, 'BenchmarkDotNet.Artifacts'),
            os.path.join(config.configuration.test_result, 'BenchmarkDotNet.Artifacts')
        )
        if rt_code == 0:
            message = 'successfully run benchmark.\n'
        else:
            message = 'fail to run benchmark!\n'
    except Exception as e:
        message = f'fail to run benchmark: {e}.\n'

    print(message)
    with open(log_path, 'a+') as log:
        log.write(message)
