"""methods for dotnet app creation and building"""

import os
import glob
from xml.etree import ElementTree as ET

import app
from tools.terminal import run_command_sync


@app.check_function_input()
@app.log_function()
def create_new_app(dotnet_bin_path: str, 
                   app_type: str,
                   app_root: str,
                   env: dict) -> str|Exception:
    """create app with dotnet command

    :param dotnet_bin_path: path to dotnet executable
    :param app_type: type of dotnet app
    :param app_root: path to the project
    :param env: required environment variable
    :return: path to the project or exception if fail to create
    """
    args = [
        dotnet_bin_path, 'new', app_type,
        '-o', app_root
    ]
    command, stdout, stderr = run_command_sync(args, env=env)
    if stderr != '':
        return Exception(f'fail to create {app_type} in {app_root}, see log for details')
    else:
        return app_root
    

@app.check_function_input()
@app.log_function()
def build_app(dotnet_bin_path: str, 
              app_root: str,
              env: dict) -> str|Exception:
    """build app with dotnet command

    :param dotnet_bin_path: path to dotnet executable
    :param app_root: path to the project
    :param env: required environment variable
    :return: path to the project or exception if fail to create
    """
    args = [
        dotnet_bin_path, 'build', '-c', 'Release'
    ]
    command, stdout, stderr = run_command_sync(args, env=env)
    if stderr != '':
        return Exception(f'fail to install tool, see log for details')
    else:
        return app_root
    

@app.check_function_input()
@app.log_function()
def change_target_framework(app_root: str, sdk_version: str):
    """change target framework of app

    :param app_root: path to the project
    :param sdk_version: version of sdk
    :return: path to the project or exception if fail to change
    """
    project_file_template = os.path.join(app_root, '*.csproj')
    project_file_candidates = glob.glob(project_file_template)

    if len(project_file_candidates) < 1:
        return Exception(f'no project file found in {app_root}')
    
    try:
        project_file = project_file_candidates[0]
        tree = ET.parse(project_file)
        root = tree.getroot()

        lang_version_element = ET.Element("LangVersion")
        lang_version_element.text = "latest"

        root.find('PropertyGroup').append(lang_version_element)
        root.find('PropertyGroup').find('TargetFramework').text = 'net' + sdk_version[:3]
        tree.write(project_file)

        return app_root
    except Exception as ex:
        return Exception(f'fail to change target framework in {app_root}: {ex}')