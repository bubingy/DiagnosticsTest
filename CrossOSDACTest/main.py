'''Run CrossOSDAC test.'''

# coding=utf-8

import os
import shutil

from infrastructure import sdk, tools
from utils.logger import ScriptLogger
from utils.sysinfo import get_cpu_arch
from project import project_oom, project_uhe
from CrossOSDACTest.config import GlobalConfig, TestConfig
from CrossOSDACTest import analyze, validate


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


def prepare_test_bed(conf: TestConfig):
    '''Create folders for TestBed.
    '''
    try:
        if not os.path.exists(conf.test_bed):
            os.makedirs(conf.test_bed)
        if not os.path.exists(conf.dump_directory):
            os.makedirs(conf.dump_directory)
        if not os.path.exists(conf.analyze_output):
            os.makedirs(conf.analyze_output)
    except Exception as e:
        print(e)
        exit(-1)


def get_remove_candidate(global_conf: GlobalConfig) -> set:
    to_be_removed = set()
    for idx, _ in enumerate(global_conf.sdk_version_list):
        for arch in ['x86', 'x64']:
            conf = global_conf.get(idx, arch)
            if 'win' in conf.rid: home_path = os.environ['USERPROFILE']
            else: home_path = os.environ['HOME']
            to_be_removed = to_be_removed.union(
                {
                    os.path.join(home_path, '.aspnet'),
                    os.path.join(home_path, '.dotnet'),
                    os.path.join(home_path, '.nuget'),
                    os.path.join(home_path, '.templateengine'),
                    os.path.join(home_path, '.lldb'),
                    os.path.join(home_path, '.lldbinit'),
                    os.path.join(home_path, '.local'),
                    os.path.join(conf.test_bed, f'dotnet-install.sh'),
                    os.path.join(conf.test_bed, f'dotnet-install.ps1'),
                    conf.dotnet_root,
                    conf.tool_root
                }
            )
    return to_be_removed


def clean(global_conf: GlobalConfig):
    to_be_removed = get_remove_candidate(global_conf)

    for f in to_be_removed:
        if not os.path.exists(f): continue
        try:
            if os.path.isdir(f): shutil.rmtree(f)
            else: os.remove(f)
        except Exception as e:
            print(f'fail to remove {f}: {e}')


def run_test(global_conf: GlobalConfig, action: str):
    global_conf = GlobalConfig()
    cpu_arch = get_cpu_arch()
    if action == 'analyze':
        '''Analyze dump on linux
        '''
        for idx, _ in enumerate(global_conf.sdk_version_list):
            conf = global_conf.get(idx, cpu_arch)
            prepare_test_bed(conf)

            logger = ScriptLogger(
                f'crossosdac-{conf.sdk_version}-{conf.rid}',
                os.path.join(
                    conf.test_bed,
                    f'crossosdac-{conf.sdk_version}-{conf.rid}.log'
                )
            )

            sdk.install_sdk_from_script(conf.sdk_version,conf.test_bed, conf.rid, cpu_arch, logger)
            if conf.rid != 'linux-musl-arm64':
                tools.install_tool('dotnet-dump', conf.tool_root, conf.tool_version, conf.tool_feed, logger)
                project_oom.create_build_oom(conf, logger)
                project_uhe.create_build_uhe(conf, logger)

            dump_path = project_oom.run_oom(conf, logger)
            logger.info(f'start analyze {dump_path}')
            analyze.analyze(conf, dump_path)

            dump_path = project_uhe.run_uhe(conf, logger)
            logger.info(f'start analyze {dump_path}')
            analyze.analyze(conf, dump_path)

            clean(global_conf)
            
    elif action == 'validate':
        '''Analyze dump on windows
        '''
        for idx, _ in enumerate(global_conf.sdk_version_list):
            for arch in ['x86', 'x64']:
                # must put `global_conf.get` in the inner loop
                conf = global_conf.get(idx, arch)
                prepare_test_bed(conf)

                logger = ScriptLogger(
                    f'crossosdac-{conf.sdk_version}-{conf.rid}-{arch}-validate',
                    os.path.join(
                        conf.test_bed,
                        f'crossosdac-{conf.sdk_version}-{conf.rid}-{arch}-validate.log'
                    )
                )

                sdk.install_sdk_from_script(conf.sdk_version,conf.test_bed, conf.rid, arch, logger)
                tools.install_tool('dotnet-dump', conf.tool_root, conf.tool_version, conf.tool_feed, logger)

                if arch == 'x86': dump_name_list = filter_32bit_dump(conf.dump_directory)
                if arch == 'x64': dump_name_list = filter_64bit_dump(conf.dump_directory)
                for dump_name in dump_name_list:
                    if 'dump_' not in dump_name: continue # not a dump file
                    dump_path = os.path.join(conf.dump_directory, dump_name)
                    output_path = os.path.join(
                        conf.analyze_output,
                        dump_name.replace('dump', 'out') + '_win'
                    )
                    logger.info(f'start analyze {dump_path}')
                    if arch == 'x86': validate.validate_32bit(conf, dump_path, output_path)
                    else: validate.validate(conf, dump_path, output_path)

                clean(global_conf)
    else:
        raise Exception(f'unknown action: {action}')
