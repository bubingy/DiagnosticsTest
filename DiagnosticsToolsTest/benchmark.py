# coding=utf-8

import os
import shutil
import logging

from DiagnosticsToolsTest import config
from project.project import change_framework
from utils.terminal import run_command_sync


def download_diagnostics(configuration: config.TestConfig, logger: logging.Logger):
    '''Clone diagnostics from github
    '''
    logger.info('download diagnostics')
    if configuration.run_benchmarks is False:
        logger.info('ignore benchmarks, so the repo won\'t be downloaded.')
        logger.info('download diagnostics finished')
        return

    command = 'git clone https://github.com/dotnet/diagnostics.git'
    outs, errs = run_command_sync(command, cwd=configuration.test_bed)
    logger.info(f'run command:\n{command}\n{outs}')
    if errs != '':
        logger.error(f'fail to download diagnostics!\n{errs}')
        logger.info('download diagnostics finished')
        return

    repo_dir = os.path.join(
        configuration.test_bed, 'diagnostics'
    )

    command = f'git reset --hard {configuration.tool_commit}'
    outs, errs = run_command_sync(command,  cwd=repo_dir)
    logger.info(f'run command:\n{command}\n{outs}')
    if errs != '':
        logger.error(f'fail to reset commit id!\n{errs}')
        logger.info('download diagnostics finished')
        return

    project_dir = os.path.join(
        repo_dir, 'src', 'tests', 'benchmarks'
    )

    change_framework(project_dir, configuration.sdk_version)

    logger.info('download diagnostics finished')


def run_benchmark(configuration: config.TestConfig, logger: logging.Logger):
    '''Run benchmark

    '''
    logger.info('run benchmark')
    if configuration.run_benchmarks is False:
        logger.info('ignore benchmarks.')
        logger.info('run benchmark finished')
        return
    project_dir = os.path.join(
        configuration.test_bed, 'diagnostics', 
        'src', 'tests', 'benchmarks'
    )

    command = f'{configuration.dotnet} run -c release'
    outs, errs = run_command_sync(command, cwd=project_dir)
    logger.info(f'run command:\n{command}\n{outs}')


    if errs == '':
        logger.info('successfully run benchmark.')
    else:
        logger.error(f'fail to run benchmark!\n{errs}')

    try:
        shutil.copytree(
            os.path.join(project_dir, 'BenchmarkDotNet.Artifacts'),
            os.path.join(configuration.test_result, 'BenchmarkDotNet.Artifacts')
        )
    except Exception as e:
        logger.error(f'fail to copy Artifacts!\n{e}')

    logger.info('run benchmark finished')
