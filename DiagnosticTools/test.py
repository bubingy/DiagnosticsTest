import os

from DiagnosticTools.configuration import DiagToolsTestConfiguration


def run_test(test_conf: DiagToolsTestConfiguration):
    os.makedirs(test_conf.testbed, exist_ok=True)