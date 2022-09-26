import os
from xml.etree import ElementTree as ET

from utils.logger import ScriptLogger
from utils.terminal import run_command_sync


def create_project(project_type: str, project_dir: os.PathLike, dotnet: os.PathLike, logger: ScriptLogger) -> bool:
    project_name = os.path.basename(project_dir)
    logger.info(f'create {project_name}')

    command = f'{dotnet} new {project_type} -o {project_dir}'
    outs, errs = run_command_sync(command)
    logger.info(f'run command:\n{command}\n{outs}')
    if errs != '':
        logger.error(f'fail to create {project_name}!\n{errs}')
        return False
    else:
        logger.info(f'successfully create {project_name}')


def change_framework(project_dir: os.PathLike, sdk_version: str):
    project_name = os.path.basename(project_dir)
    project_file = os.path.join(project_dir, f'{project_name}.csproj')
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


def build_project(project_dir: os.PathLike, dotnet: os.PathLike, rid: str, logger: ScriptLogger, source_feed: str=None) -> bool:
    project_name = os.path.basename(project_dir)

    logger.info(f'build {project_name}')
    if source_feed != None:
        command = f'{dotnet} build -o out --source {source_feed}'
        outs, errs = run_command_sync(command, cwd=project_dir)
        logger.info(f'run command:\n{command}\n{outs}')
        if errs == '' and 'Build FAILED' not in outs:
            logger.info(f'successfully build {project_name}.')
            return True
    
    command = f'{dotnet} build -o out -r {rid}'
    outs, errs = run_command_sync(command, cwd=project_dir)
    logger.info(f'run command:\n{command}\n{outs}')
    if errs == ''  and 'Build FAILED' not in outs:
        logger.info(f'successfully build {project_name}.')
        return True
    
    # if given runtime isn't available, try to publish without specifying rid.
    command = f'{dotnet} build -o out'
    outs, errs = run_command_sync(command, cwd=project_dir)
    logger.info(f'run command:\n{command}\n{outs}')
    if errs == ''  and 'Build FAILED' not in outs:
        logger.info(f'successfully build {project_name}.')
        return True
    else:
        logger.error(f'fail to build {project_name}!\n{errs}')
        return False