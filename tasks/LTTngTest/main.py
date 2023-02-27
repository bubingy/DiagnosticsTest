import os
import shutil

import instances.constants as constants
import instances.config.LTTngTest as lttng_test_conf
from instances.logger import ScriptLogger
from services.terminal import run_command_sync
from services.project import gcperfsim as gcperfsim_service
from services.dotnet import sdk as sdk_service, tools as tools_service
from services.config.LTTngTest import load_lttngtestconf


def prepare_test_bed():
    '''Create folders for TestBed.
    '''
    try:
        if not os.path.exists(lttng_test_conf.testbed):
            os.makedirs(lttng_test_conf.testbed)
        if not os.path.exists(lttng_test_conf.test_result_root):
            os.makedirs(lttng_test_conf.test_result_root)
    except Exception as e:
        print(f'fail to create folders: {e}')
        exit(-1)


def run_test():
    load_lttngtestconf(
        os.path.join(
            constants.configuration_root,
            'LTTngTest.conf'
        )
    )
    prepare_test_bed()

    logger = ScriptLogger(
        'perfcollect',
        os.path.join(lttng_test_conf.test_result_root, 'perfcollect.log')
    )
    tools_service.download_perfcollect(lttng_test_conf.testbed, logger)
    perfcollect_path = os.path.join(lttng_test_conf.testbed, 'perfcollect')
    
    for sdk_version in lttng_test_conf.sdk_version_list:
        env = os.environ.copy()
        dotnet_root = os.path.join(
            lttng_test_conf.testbed,
            f'dotnet-sdk-{sdk_version}'
        )

        env['DOTNET_ROOT'] = dotnet_root
        env['PATH'] = f'{dotnet_root}:' + env['PATH']
        
        sdk_service.install_sdk_from_script(
            sdk_version,
            lttng_test_conf.testbed,
            dotnet_root,
            lttng_test_conf.rid,
            arch=None,
            logger=logger
        )

        gcperfsim_service.create_build_gcperfsim(
            lttng_test_conf.testbed,
            os.path.join(dotnet_root, 'dotnet'),
            env,
            sdk_version,
            logger
        )

        gcperfsim_service.run_gcperfsim(
            env, 
            lttng_test_conf.testbed
        )

        trace_path = os.path.join(
            lttng_test_conf.test_result_root,
            f'trace_net{sdk_version}_{lttng_test_conf.rid}'
        )

        command = f'/bin/bash {perfcollect_path} collect {trace_path} -collectsec 30'
        outs, errs = run_command_sync(command, env=env)
        logger.info(f'run command:\n{command}\n{outs}')
        if errs != '':
            logger.error(f'fail to collect trace!\n{errs}')
        logger.info(f'collection finished')

        clean()


def clean() -> None:
    home_path = os.environ['HOME']
    to_be_removed = [
        os.path.join(home_path, '.debug'),
        os.path.join(home_path, '.dotnet'),
        os.path.join(home_path, '.nuget'),
        os.path.join(home_path, 'lttng-traces'),
        os.path.join(home_path, '.local')
    ]
    
    for f in to_be_removed:
        if not os.path.exists(f): continue
        try:
            if os.path.isdir(f): shutil.rmtree(f)
            else: os.remove(f)
        except Exception as e:
            print(f'fail to remove {f}: {e}')

    