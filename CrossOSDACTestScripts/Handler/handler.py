'''Handle scenarios on linux and windows.'''

# coding=utf-8

import os

import init
from config import GlobalConfig
from Projects import project
from Handler import analyze, validate


def analyze_on_linux(global_conf: GlobalConfig):
    '''Analyze dump on linux
    '''
    for idx, _ in enumerate(global_conf.sdk_version_list):
        conf = global_conf.get(idx)
        init.prepare_test_bed(conf)
        init.install_sdk(conf)
        if conf.rid != 'linux-musl-arm64':
            init.install_tools(conf)
        for project_name in ['uhe', 'oom']:
            if conf.rid != 'linux-musl-arm64':
                project.create_publish_project(conf, project_name)
            dump_path = project.run_project(conf, project_name)
            analyze.analyze(conf, dump_path)


def validate_on_windows(arch: str):
    '''Analyze dump on windows
    '''
    init.prepare_test_bed()
    init.install_sdk(arch)
    init.install_tools()
    # for dump_name in os.listdir(configuration.dump_directory):
    #     if 'dump_' not in dump_name: continue # not a dump file
    #     dump_path = os.path.join(configuration.dump_directory, dump_name)
    #     output_path = os.path.join(
    #         configuration.analyze_output,
    #         dump_name.replace('dump', 'out') + '_win'
    #     ) 
    #     if 'linux-arm' in dump_name and '64' not in dump_name:
    #         validate.validate_32bit(dump_path, output_path)
    #     else:
    #         validate.validate(dump_path, output_path)
