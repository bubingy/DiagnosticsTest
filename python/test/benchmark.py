# coding=utf-8

import os
import shutil
from xml.etree import ElementTree as ET

from config import configuration
from utils import run_command_sync, Result

log_path = os.path.join(configuration.test_result, 'benchmark.log')


def download_diagnostics()->Result:
    '''Clone diagnostics from github
    '''
    rt_code = run_command_sync(
        'git clone https://github.com/dotnet/diagnostics.git',
        log_path=log_path,
        cwd=configuration.test_bed
    )
    if rt_code != 0:
        return Result(rt_code, 'fail to download diagnostics', None)

    repo_dir = os.path.join(
        configuration.test_bed, 'diagnostics'
    )
    rt_code = run_command_sync(
        f'git reset --hard {configuration.tool_commit}',
        log_path=log_path,
        cwd=repo_dir
    )
    if rt_code != 0:
        return Result(rt_code, 'fail to reset commit id', None)

    project_dir = os.path.join(
        repo_dir, 'src', 'tests', 'benchmarks'
    )
    project_file = os.path.join(project_dir, 'benchmarks.csproj')
    try:
        tree = ET.parse(project_file)
        root = tree.getroot()
        root.find('PropertyGroup').find('TargetFramework').text = \
            f'netcoreapp{configuration.sdk_version[:3]}'
        tree.write(project_file)
        return Result(0, 'successfully config benchmark', project_dir)
    except Exception as e:
        return Result(-1, 'fail to config benchmark', e)
    

def run_benchmark()->Result:
    '''Run benchmark

    '''
    project_dir = os.path.join(
        configuration.test_bed, 'diagnostics', 
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
            os.path.join(configuration.test_result, 'BenchmarkDotNet.Artifacts')
        )
        if rt_code == 0:
            return Result(0, 'successfully run benchmark', None)
        else:
            return Result(rt_code, 'fail to run benchmark', None)
    except Exception as e:
        return Result(-1, 'fail to run benchmark', e)
    