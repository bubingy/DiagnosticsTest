import os
import shutil

from infrastructure.dotnet import sdk, tools
from utils.logger import ScriptLogger
from project import project_gcperfsim
from LTTngTest.config import GlobalConfig, TestConfig


def prepare_test_bed(conf: TestConfig):
    '''Create folders for TestBed.
    '''
    try:
        if not os.path.exists(conf.test_bed):
            os.makedirs(conf.test_bed)
        if not os.path.exists(conf.trace_directory):
            os.makedirs(conf.trace_directory)
    except Exception as e:
        print(f'fail to create folders: {e}')
        exit(-1)


def run_test(global_conf: GlobalConfig):
    for idx, _ in enumerate(global_conf.sdk_version_list):
        configuration = global_conf.get(idx)
        prepare_test_bed(configuration)
        logger = ScriptLogger(
            f'lttng-{configuration.sdk_version}-{configuration.rid}',
            os.path.join(
                configuration.test_bed,
                f'lttng-{configuration.sdk_version}-{configuration.rid}.log'
            )
        )
        sdk.install_sdk(
            configuration.sdk_version,
            configuration.sdk_build_id,
            configuration.test_bed,
            configuration.rid,
            configuration.authorization,
            logger
        )
        tools.download_perfcollect(configuration.test_bed, logger)

        project_gcperfsim.create_build_gcperfsim(configuration, logger)
        proc = project_gcperfsim.run_gcperfsim(configuration)
        project_gcperfsim.collect_trace(configuration, logger)
        proc.terminate()
        proc.communicate()
        clean(global_conf)


def get_remove_candidate(global_conf: GlobalConfig) -> set:
    to_be_removed = set()
    for idx, _ in enumerate(global_conf.sdk_version_list):
        conf = global_conf.get(idx)
        if 'win' in conf.rid: home_path = os.environ['USERPROFILE']
        else: home_path = os.environ['HOME']
        to_be_removed = to_be_removed.union(
            {
                conf.dotnet_root,
                os.path.join(
                    conf.test_bed,
                    f'gcperfsim'
                )
            }
        )
        for f in os.listdir(conf.trace_directory):
            f_path = os.path.join(conf.trace_directory, f)
            if os.path.isdir(f_path): to_be_removed.add(f_path)

    to_be_removed = to_be_removed.union(
        {
            os.path.join(home_path, '.debug'),
            os.path.join(home_path, '.dotnet'),
            os.path.join(home_path, '.nuget'),
            os.path.join(home_path, 'lttng-traces'),
            os.path.join(home_path, '.local'),
            conf.dotnet_root
        }
    )
    return to_be_removed


def clean(global_conf: GlobalConfig) -> None:
    to_be_removed = get_remove_candidate(global_conf)
    for f in to_be_removed:
        if not os.path.exists(f): continue
        try:
            if os.path.isdir(f): shutil.rmtree(f)
            else: os.remove(f)
        except Exception as e:
            print(f'fail to remove {f}: {e}')

    