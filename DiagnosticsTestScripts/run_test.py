# coding=utf-8

import os

import init
import utils
import config
from project import projects
from test import benchmark
from test import dotnet_counters
from test import dotnet_dump
from test import dotnet_gcdump
from test import dotnet_sos
from test import dotnet_trace

if __name__ == '__main__':
    config.configuration = config.TestConfig()
    config.configuration.prepare_test_bed()

    logger = utils.create_logger(
        'initialize',
        os.path.join(
            config.configuration.test_result,
            'init.log'
        )
    )
    init.install_sdk(config.configuration, logger)
    # init.install_tools(config.configuration, logger)

    # logger = utils.create_logger(
    #     'projects',
    #     os.path.join(
    #         config.configuration.test_result,
    #         'projects.log'
    #     )
    # )
    # projects.create_publish_consoleapp(config.configuration, logger)
    # projects.create_publish_GCDumpPlayground(config.configuration, logger)
    # projects.create_publish_webapp(config.configuration, logger)

    # logger = utils.create_logger(
    #     'benchmark',
    #     os.path.join(
    #         config.configuration.test_result,
    #         'benchmark.log'
    #     )
    # )
    # benchmark.download_diagnostics(config.configuration, logger)
    # benchmark.run_benchmark(config.configuration, logger)

    # logger = utils.create_logger(
    #     'dotnet_counters',
    #     os.path.join(
    #         config.configuration.test_result,
    #         'dotnet_counters.log'
    #     )
    # )
    # dotnet_counters.test_dotnet_counters(config.configuration, logger)
    
    # logger = utils.create_logger(
    #     'dotnet_dump',
    #     os.path.join(
    #         config.configuration.test_result,
    #         'dotnet_dump.log'
    #     )
    # )
    # dotnet_dump.test_dotnet_dump(config.configuration, logger)
    
    # logger = utils.create_logger(
    #     'dotnet_gcdump',
    #     os.path.join(
    #         config.configuration.test_result,
    #         'dotnet_gcdump.log'
    #     )
    # )
    # dotnet_gcdump.test_dotnet_gcdump(config.configuration, logger)
    
    # logger = utils.create_logger(
    #     'dotnet_sos',
    #     os.path.join(
    #         config.configuration.test_result,
    #         'dotnet_sos.log'
    #     )
    # )
    # dotnet_sos.test_dotnet_sos(config.configuration, logger)

    # logger = utils.create_logger(
    #     'dotnet_trace',
    #     os.path.join(
    #         config.configuration.test_result,
    #         'dotnet_trace.log'
    #     )
    # )
    # dotnet_trace.test_dotnet_trace(config.configuration, logger)
