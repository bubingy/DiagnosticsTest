'''Create, build and run app for diag tools testing'''

import os
import shutil

import app
from tools import dotnet_app


@app.function_monitor(pre_run_msg='create and build console app for diag tool test.')
def create_build_console_app(dotnet_bin_path: str, app_root: str, env: dict) -> str|Exception:
    """create and build console app

    :param dotnet_bin_path: path to dotnet executable
    :param app_root: path to the project
    :param env: required environment variable
    :return: path to the project or exception if fail to create
    """
    # create app
    app_root = dotnet_app.create_new_app(dotnet_bin_path, 'console', app_root, env)
    if isinstance(app_root, Exception):
        return app_root

    # modify Program.cs
    src_code_path = os.path.join(
        app.script_root,
        'DiagnosticTools',
        'assets',
        'consoleapp',
        'Program.cs'
    )
    dest_code_path = os.path.join(app_root, 'Program.cs')
    try:
        shutil.copy(src_code_path, dest_code_path)
    except Exception as ex:
        return Exception(f'fail to modify console app source code: {ex}')
    # build app 
    app_root = dotnet_app.build_app(dotnet_bin_path, app_root, env)
    return app_root