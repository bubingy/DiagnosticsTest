# coding=utf-8

import os
import shutil
import logging
from xml.etree import ElementTree as ET

import config
from utils import run_command_sync


def download_diagnostics(configuration: config.TestConfig, logger: logging.Logger):
    '''Clone diagnostics from github
    '''
    logger.info('****** download diagnostics ******')
    if configuration.run_benchmarks is False:
        logger.info('ignore benchmarks, so the repo won\'t be downloaded.')
        logger.info('****** download diagnostics finished ******')
        return
    rt_code = run_command_sync(
        'git clone https://github.com/dotnet/diagnostics.git',
        logger,
        cwd=configuration.test_bed
    )
    if rt_code != 0:
        logger.error('fail to download diagnostics!')
        logger.info('****** download diagnostics finished ******')
        return

    repo_dir = os.path.join(
        configuration.test_bed, 'diagnostics'
    )
    rt_code = run_command_sync(
        f'git reset --hard {configuration.tool_commit}',
        logger,
        cwd=repo_dir
    )
    if rt_code != 0:
        logger.error('fail to reset commit id!')
        logger.info('****** download diagnostics finished ******')
        return

    project_dir = os.path.join(
        repo_dir, 'src', 'tests', 'benchmarks'
    )
    project_file = os.path.join(project_dir, 'benchmarks.csproj')

    tree = ET.parse(project_file)
    root = tree.getroot()
    root.find('PropertyGroup').find('TargetFramework').text = \
        f'netcoreapp{configuration.sdk_version[:3]}'
    tree.write(project_file)

    logger.info('****** download diagnostics finished ******')


def run_benchmark(configuration: config.TestConfig, logger: logging.Logger):
    '''Run benchmark

    '''
    logger.info('****** run benchmark ******')
    if configuration.run_benchmarks is False:
        logger.info('ignore benchmarks.')
        logger.info('****** run benchmark finished ******')
        return
    project_dir = os.path.join(
        configuration.test_bed, 'diagnostics', 
        'src', 'tests', 'benchmarks'
    )

    rt_code = run_command_sync(
        f'{configuration.dotnet} run -c release',
        logger,
        cwd=project_dir
    )
    shutil.copytree(
        os.path.join(project_dir, 'BenchmarkDotNet.Artifacts'),
        os.path.join(configuration.test_result, 'BenchmarkDotNet.Artifacts')
    )
    if rt_code == 0:
        logger.info('successfully run benchmark.')
    else:
        logger.error('fail to run benchmark!')

    logger.info('****** run benchmark finished ******')
