# coding=utf-8

import init
from project import projects
from test import benchmark
from test import dotnet_counters
from test import dotnet_dump
from test import dotnet_gcdump
from test import dotnet_sos
from test import dotnet_trace
from utils import clean

if __name__ == '__main__':
    init.prepare_test_bed()
    init.install_sdk()
    init.install_tools()

    projects.create_publish_consoleapp()
    projects.create_publish_GCDumpPlayground()
    projects.create_publish_webapp()

    benchmark.download_diagnostics()
    benchmark.run_benchmark()

    dotnet_counters.test_counters()
    dotnet_dump.test_dump()
    dotnet_gcdump.test_gcdump()
    dotnet_sos.test_sos()
    dotnet_trace.test_trace()
    clean()
