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
    init.install_sdk()
    if configuration.rid != 'linux-musl-arm64':
        init.install_tools()
    for project_name in ['uhe', 'oom']:
        if configuration.rid != 'linux-musl-arm64':
            project.create_publish_project(project_name)
        dump_path = project.run_project(project_name)
        analyze.analyze(dump_path)


def validate_on_windows(dump_path: os.PathLike, output_path: os.PathLike):
    '''Analyze dump on windows
    '''
    if configuration.rid is 'linux-arm':
        validate.validate_32bit(dump_path, output_path)
    else:
        validate.validate(dump_path, output_path)
