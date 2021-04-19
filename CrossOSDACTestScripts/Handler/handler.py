'''Handle scenarios on linux and windows.'''

# coding=utf-8

import os

import init
from config import configuration
from Projects import project
from Handler import analyze, validate


def analyze_on_linux():
    '''Analyze dump on linux
    '''
    init.prepare_test_bed()
    init.install_sdk()
    if configuration.rid != 'linux-musl-arm64':
        init.install_tools()
    for project_name in ['uhe', 'oom']:
        if configuration.rid != 'linux-musl-arm64':
            project.create_publish_project(project_name)
        dump_path = project.run_project(project_name)
        analyze.analyze(dump_path)


def init_on_windows(arch: str):
    '''Install sdk and tool on Windows.
    '''
    init.prepare_test_bed()
    init.install_sdk(arch)
    init.install_tools()


def validate_on_windows(dump_path: os.PathLike, output_path: os.PathLike):
    '''Analyze dump on windows
    '''
    if os.path.isdir(dump_path):
        assert os.path.isdir(dump_path) and os.path.isdir(output_path)
        for dump_name in os.listdir(dump_path):
            if 'dump_net' not in dump_name: continue # not a dump file
            full_dump_path = os.path.join(dump_path, dump_name)
            full_out_path = os.path.join(
                output_path,
                dump_name.replace('dump', 'out') + '_win'
            ) 
            if 'linux-arm' in dump_path:
                validate.validate_32bit(full_dump_path, full_out_path)
            else:
                validate.validate(full_dump_path, full_out_path)

    if os.path.isfile(dump_path):
        assert os.path.isfile(dump_path) and os.path.isfile(output_path)
        if 'linux-arm' in dump_path:
            validate.validate_32bit(dump_path, output_path)
        else:
            validate.validate(dump_path, output_path)
