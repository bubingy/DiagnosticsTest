# coding=utf-8

from AutomationScripts import init
from AutomationScripts.project import projects
from AutomationScripts.test import benchmark
from AutomationScripts.test import dotnet_counters
from AutomationScripts.test import dotnet_dump
from AutomationScripts.test import dotnet_gcdump
from AutomationScripts.test import dotnet_sos
from AutomationScripts.test import dotnet_trace
from AutomationScripts.utils import clean

def run_test():
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
