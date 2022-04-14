import os
import shutil

from DiagnosticsToolsTest import config
from project.project import create_project, change_framework, build_project
from utils.logger import ScriptLogger


def create_build_consoleapp(configuration: config.TestConfig, logger: ScriptLogger):
    '''Create and publish a dotnet console app.

    The console app is used to test startup feature of
        dotnet-counters/dotnet-trace.
    '''
    project_dir = os.path.join(configuration.test_bed, 'consoleapp')
    configuration.run_consoleapp = create_project('console', project_dir, configuration.dotnet, logger)
    change_framework(project_dir, configuration.sdk_version)
    shutil.copy(
        os.path.join(configuration.work_dir, 'project', 'consoleapp_tmp'), 
        os.path.join(project_dir, 'Program.cs')
    )

    configuration.run_consoleapp = build_project(project_dir, configuration.dotnet, configuration.rid, logger)

