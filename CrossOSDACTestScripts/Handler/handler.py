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


def validate_on_windows():
    '''Analyze dump on windows
    '''
    for dump_name in os.listdir(configuration.dump_directory):
        if 'dump_net' not in dump_name: continue # not a dump file
        dump_path = os.path.join(configuration.dump_directory, dump_name)
        output_path = os.path.join(
            configuration.analyze_output,
            dump_name.replace('dump', 'out') + '_win'
        ) 
        if 'linux-arm' in dump_name and '64' not in dump_name:
            validate.validate_32bit(dump_path, output_path)
        else:
            validate.validate(dump_path, output_path)
