import argparse

from services.sysinfo import get_rid
from services.container import run_in_container
from services.dotnet.cleaner import remove_test_temp_directory
from tasks.DiagnosticToolsTest.main import run_test


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument(
        'action',
        choices=['clean', 'deploy', 'run']
    )
    args = parser.parse_args()

    if args.action == 'clean':
        remove_test_temp_directory(get_rid())
    if args.action == 'deploy':
        run_in_container('python3 test_diagnostic_tools.py run')
    if args.action == 'run':
        run_test()
