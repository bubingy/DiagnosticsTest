import os
import glob
from xml.etree import ElementTree as ET

from instances.logger import ScriptLogger
from services.terminal import run_command_sync, PIPE


def create_project(project_name: str,
                    project_type: str,
                    project_dir: os.PathLike, 
                    dotnet_bin_path: os.PathLike,
                    env: dict,
                    logger: ScriptLogger) -> bool:
    logger.info(f'create {project_name} in {project_dir}')

    command = f'{dotnet_bin_path} new {project_type} -n {project_name} -o {project_dir}'
    outs, errs = run_command_sync(
        command,
        env=env,
        stdout=PIPE,
        stderr=PIPE
    )
    logger.info(f'run command:\n{command}\n{outs}')
    if errs != '':
        logger.error(f'fail to create {project_name}!\n{errs}')
        return False
    else:
        logger.info(f'successfully create {project_name}')
        return True


def change_framework(project_dir: os.PathLike, sdk_version: str):
    # project_name = os.path.basename(project_dir)
    print(project_dir)
    project_file = glob.glob(f'{project_dir}/*.csproj')[0]
    tree = ET.parse(project_file)
    root = tree.getroot()
    if sdk_version[0] == '3':
        framework = 'netcoreapp' + sdk_version[:3]
    else:
        framework = 'net' + sdk_version[:3]

    lang_version_element = ET.Element("LangVersion")
    lang_version_element.text = "latest"

    root.find('PropertyGroup').append(lang_version_element)
    root.find('PropertyGroup').find('TargetFramework').text = framework
    tree.write(project_file)


def build_project(project_dir: os.PathLike, 
                    dotnet_bin_path: os.PathLike,
                    env: dict,
                    logger: ScriptLogger, 
                    source_feed: str=None) -> bool:
    project_name = os.path.basename(project_dir)

    logger.info(f'build {project_name}')
    if source_feed != None:
        command = f'{dotnet_bin_path} build -o out --source {source_feed}'
        outs, errs = run_command_sync(
            command,
            env=env,
            cwd=project_dir,
            stdout=PIPE,
            stderr=PIPE
        )
        logger.info(f'run command:\n{command}\n{outs}')
        if errs == '' and 'Build FAILED' not in outs:
            logger.info(f'successfully build {project_name}.')
            return True
    
    # if given runtime isn't available, try to publish without specifying rid.
    command = f'{dotnet_bin_path} build -o out'
    outs, errs = run_command_sync(
        command,
        env=env,
        cwd=project_dir,
        stdout=PIPE,
        stderr=PIPE
    )
    logger.info(f'run command:\n{command}\n{outs}')
    if errs == ''  and 'Build FAILED' not in outs:
        logger.info(f'successfully build {project_name}.')
        return True
    else:
        logger.error(f'fail to build {project_name}!\n{errs}')
        return False
