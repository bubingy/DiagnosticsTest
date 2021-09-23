# coding=utf-8

import config

# must init `config.configuration` before
# importing other modules.
config.configuration = config.TestConfig()

import init
from project import projects
from test import benchmark
from test import dotnet_counters
from test import dotnet_dump
from test import dotnet_gcdump
from test import dotnet_sos
from test import dotnet_trace


init.prepare_test_bed()
init.install_sdk()
init.install_tools()

projects.create_publish_consoleapp()
projects.create_publish_GCDumpPlayground()
projects.create_publish_webapp()

benchmark.download_diagnostics()
benchmark.run_benchmark()

dotnet_counters.test_dotnet_counters()
dotnet_dump.test_dotnet_dump()
dotnet_gcdump.test_dotnet_gcdump()
dotnet_sos.test_dotnet_sos()
dotnet_trace.test_dotnet_trace()
