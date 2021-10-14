'''Handle scenarios on linux and windows.'''

# coding=utf-8

import os
import platform

import init
from config import GlobalConfig
from Projects import project
from Handler import analyze, validate


def analyze_on_linux(global_conf: GlobalConfig):
    '''Analyze dump on linux
    '''
    machine_type = platform.machine().lower()
    if machine_type in ['x86_64', 'amd64']:
        arch = 'x64'
    elif machine_type in ['aarch64']:
        arch = 'arm64'
    elif machine_type in ['armv7l']:
        arch = 'arm'
    else:
        raise Exception(f'unsupported machine type: {machine_type}')

    for idx, _ in enumerate(global_conf.sdk_version_list):
        conf = global_conf.get(idx, arch)
        init.prepare_test_bed(conf)
        init.install_sdk(conf)
        if conf.rid != 'linux-musl-arm64':
            init.install_tools(conf)
        for project_name in ['uhe', 'oom']:
            if conf.rid != 'linux-musl-arm64':
                project.create_publish_project(conf, project_name)
            dump_path = project.run_project(conf, project_name)
            analyze.analyze(conf, dump_path)


def filter_32bit_dump(dump_directory: os.PathLike) -> list:
    return list(
        filter(
            lambda dump_name: 'linux-arm' in dump_name and '64' not in dump_name,
            os.listdir(dump_directory)
        )
    )


def filter_64bit_dump(dump_directory: os.PathLike) -> list:
    return list(
        filter(
            lambda dump_name: 'x64' in dump_name or 'arm64' in dump_name ,
            os.listdir(dump_directory)
        )
    )


def validate_on_windows(global_conf: GlobalConfig):
    '''Analyze dump on windows
    '''
    for idx, _ in enumerate(global_conf.sdk_version_list):
        for arch in ['x86', 'x64']:
            # must put `global_conf.get` in the inner loop
            conf = global_conf.get(idx, arch)
            init.prepare_test_bed(conf)
            init.install_sdk(conf, arch)
            init.install_tools(conf)

            if arch == 'x86': dump_name_list = filter_32bit_dump(conf.dump_directory)
            if arch == 'x64': dump_name_list = filter_64bit_dump(conf.dump_directory)
            for dump_name in dump_name_list:
                if 'dump_' not in dump_name: continue # not a dump file
                dump_path = os.path.join(conf.dump_directory, dump_name)
                output_path = os.path.join(
                    conf.analyze_output,
                    dump_name.replace('dump', 'out') + '_win'
                )
                if arch == 'x86': validate.validate_32bit(conf, dump_path, output_path)
                else: validate.validate(dump_path, output_path)
