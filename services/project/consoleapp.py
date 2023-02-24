import os
import shutil

import instances.constants as constants
from services.project.project import create_project, change_framework, build_project
from instances.logger import ScriptLogger
from instances.project import consoleapp


def create_build_consoleapp(test_bed: str, dotnet_bin_path: str, sdk_version: str, env: dict, logger: ScriptLogger):
    '''Create and publish a dotnet console app.

    The console app is used to test startup feature of
        dotnet-counters/dotnet-trace.
    '''
    consoleapp.project_root = os.path.join(test_bed, 'consoleapp')
    consoleapp.runnable = create_project(
        'console',
        consoleapp.project_root,
        dotnet_bin_path,
        env,
        logger
    )
    change_framework(consoleapp.project_root, sdk_version)
    shutil.copy(
        os.path.join(constants.script_root, 'assets', 'Program.cs'), 
        os.path.join(consoleapp.project_root, 'Program.cs')
    )

    consoleapp.runnable = consoleapp.runnable and build_project(
        consoleapp.project_root,
        dotnet_bin_path,
        env,
        logger
    )

    ext = os.path.splitext(dotnet_bin_path)[-1]
    consoleapp.project_bin_path = os.path.join(consoleapp.project_root, 'out', f'consoleapp{ext}')
    logger.info('create consoleapp finished')
