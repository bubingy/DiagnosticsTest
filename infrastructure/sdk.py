'''Install .NET SDK'''

import os
import gzip
from urllib import request

from utils.terminal import run_command_sync
from utils.logger import ScriptLogger
from utils.azure import get_artifact
from utils.sysinfo import get_cpu_arch


def get_sdk_download_link(sdk_version: str, sdk_build_id: str, rid: str, authorization: str, logger: ScriptLogger) -> str:
    '''Get PackageArtifacts according to the given `build`.

    :return: download link of sdk.
    '''
    logger.info('query sdk download link')
    try:
        artifact = get_artifact(sdk_build_id, authorization, artifact_name='AssetManifests')
    except Exception as e:
        logger.error(f'fail to get download link: {e}')
        raise Exception(f'fail to get download link: {e}')
    container_id = artifact['resource']['data'].split('/')[1]
    if 'win' in rid: suffix = 'zip'
    else: suffix = 'tar.gz'
    if 'servicing' in sdk_version or 'rtm' in sdk_version:
        version_number = sdk_version.split('-')[0]
        sdk_download_link = (
            f'https://dev.azure.com/dnceng/_apis/resources/Containers/{container_id}/'
            f'BlobArtifacts?itemPath=BlobArtifacts/dotnet-sdk-{version_number}-{rid}.{suffix}'
        )
    else:
        sdk_download_link = (
            f'https://dev.azure.com/dnceng/_apis/resources/Containers/{container_id}/'
            f'BlobArtifacts?itemPath=BlobArtifacts/dotnet-sdk-{sdk_version}-{rid}.{suffix}'
        )
    
    logger.info(f'sdk download link: {sdk_download_link}')
    return sdk_download_link


def install_sdk_from_script(sdk_version: str, test_bed: os.PathLike, rid: str, arch: str, logger: ScriptLogger):
    logger.info(f'download dotnet install script')
    dotnet_root = os.environ['DOTNET_ROOT']
    if 'win' in rid:
        script_download_link = 'https://dot.net/v1/dotnet-install.ps1'
        script_engine = 'powershell.exe'

    else:
        script_download_link = 'https://dotnet.microsoft.com/download/dotnet/scripts/v1/dotnet-install.sh'
        script_engine = '/bin/bash'

    script_path = os.path.join(test_bed, os.path.basename(script_download_link))
    req = request.urlopen(script_download_link)
    with open(script_path, 'w+') as f:
        f.write(req.read().decode())

    if 'win' not in rid:
        run_command_sync(f'chmod +x {script_path}')

    command = f'{script_engine} {script_path} -InstallDir {dotnet_root} -v {sdk_version} -Architecture {arch}'
    outs, errs = run_command_sync(command)
    logger.info(f'run command:\n{command}\n{outs}')
    
    if errs != '':
        logger.error(f'fail to install .net SDK {sdk_version}!\n{errs}')
        exit(-1)


def install_runtime_from_script(runtime_version: str, test_bed: os.PathLike, rid: str, logger: ScriptLogger):
    logger.info(f'download dotnet install script')
    dotnet_root = os.environ['DOTNET_ROOT']
    if 'win' in rid:
        script_download_link = 'https://dot.net/v1/dotnet-install.ps1'
        script_engine = 'powershell.exe'

    else:
        script_download_link = 'https://dotnet.microsoft.com/download/dotnet/scripts/v1/dotnet-install.sh'
        script_engine = '/bin/bash'

    script_path = os.path.join(test_bed, os.path.basename(script_download_link))
    req = request.urlopen(script_download_link)
    with open(script_path, 'w+') as f:
        f.write(req.read().decode())

    if 'win' not in rid:
        run_command_sync(f'chmod +x {script_path}')

    command = f'{script_engine} {script_path} -InstallDir {dotnet_root} -v {runtime_version} --runtime dotnet'
    outs, errs = run_command_sync(command)
    logger.info(f'run command:\n{command}\n{outs}')
    
    if errs != '':
        logger.error(f'fail to install .net runtime {runtime_version}!\n{errs}')
        exit(-1)


def install_sdk_from_Azure(sdk_version: str, sdk_build_id: str, test_bed: os.PathLike, rid: str, authorization: str, logger: ScriptLogger):
    sdk_download_link = get_sdk_download_link(sdk_version, sdk_build_id, rid, authorization, logger)
    compressed_file_path = os.path.join(
        test_bed,
        os.path.basename(sdk_download_link)
    )
    BUFFERSIZE = 64*1024*1024

    logger.info(f'download sdk package from Azure')
    try:
        response = request.urlopen(
            request.Request(
                sdk_download_link,
                headers={
                    'Authorization': f'Basic {authorization}'
                },
            )
        )
        with open(compressed_file_path, 'wb+') as fs:
            while True:
                buffer = response.read(BUFFERSIZE)
                if buffer == b'' or len(buffer) == 0: break
                fs.write(buffer)
    except Exception as e:
        logger.error(f'fail to download package from Azure: {e}')
        if os.path.exists(compressed_file_path): os.remove(compressed_file_path)
        raise Exception(f'fail to download package from Azure: {e}')

    logger.info(f'decompress downloaded sdk package')
    decompressed_file_path = os.path.join(
        test_bed,
        os.path.splitext(compressed_file_path)[0]
    )
    try:
        with gzip.open(compressed_file_path, 'rb') as comp_ref, \
            open(decompressed_file_path, 'wb+') as decomp_ref:
            while True:
                buffer = comp_ref.read(BUFFERSIZE)
                if buffer == b'' or len(buffer) == 0: break
                decomp_ref.write(buffer)
    except Exception as e:
        logger.error(f'fail to decompress downloaded package: {e}')
        if os.path.exists(decompressed_file_path): os.remove(decompressed_file_path)
        raise Exception(f'fail to decompress downloaded package: {e}')
    finally:
        os.remove(compressed_file_path)

    dotnet_root = os.environ['DOTNET_ROOT']
    logger.info(f'extract decompressed package')
    try:
        if not os.path.exists(dotnet_root): os.makedirs(dotnet_root)
        if 'win' in rid:
            import zipfile
            with zipfile.ZipFile(decompressed_file_path, 'r') as zip_ref:
                zip_ref.extractall(dotnet_root)
        else:
            import tarfile
            with tarfile.open(decompressed_file_path, 'r') as tar_ref:
                tar_ref.extractall(dotnet_root)
    except Exception as e:
        logger.error(f'fail to extract file: {e}')
        raise Exception(f'fail to extract file: {e}')
    finally:
        logger.info(f'remove temp files')
        os.remove(decompressed_file_path)


def install_sdk(sdk_version: str, sdk_build_id: str, test_bed: os.PathLike, rid: str, authorization: str, logger: ScriptLogger):
    logger.info('install .NET sdk')
    if sdk_build_id == '':
        cpu_arch = get_cpu_arch()
        install_sdk_from_script(sdk_version, test_bed, rid, cpu_arch, logger)
    else:
        install_sdk_from_Azure(sdk_version, sdk_build_id, test_bed, rid, authorization, logger)
    logger.info('install .NET sdk finished')