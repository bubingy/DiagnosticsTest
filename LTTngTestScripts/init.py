'''Install sdk and tools
'''

import os
import sys
import gzip
import json
from urllib import request

from config import TestConfig
from utils import run_command_sync


def prepare_test_bed(conf: TestConfig):
    '''Create folders for TestBed.
    '''
    print(f'****** create folders ******')
    try:
        if not os.path.exists(conf.test_bed):
            os.makedirs(conf.test_bed)
        if not os.path.exists(conf.trace_directory):
            os.makedirs(conf.trace_directory)
    except Exception as e:
        print(f'fail to create folders: {e}')
        exit(-1)


def download_perfcollect(conf: TestConfig):
    '''Download perfcollect script.
    '''
    print(f'****** download perfcollect script ******')
    req = request.urlopen(
        'https://raw.githubusercontent.com/microsoft/perfview/main/src/perfcollect/perfcollect'
    )
    with open(f'{conf.test_bed}/perfcollect', 'w+') as f:
        f.write(req.read().decode())
    run_command_sync(f'chmod +x {conf.test_bed}/perfcollect')


def get_sdk_download_link(configuration: TestConfig) -> str:
    '''Get PackageArtifacts according to the given `build`.

    :return: download link of sdk.
    '''
    url = (
        'https://dev.azure.com/dnceng/internal/_apis/'
        f'build/builds/{configuration.sdk_build_id}/artifacts?'
        'artifactName=BlobArtifacts&api-version=6.1-preview.5'
    )
    response = request.urlopen(
        request.Request(
            url,
            headers={
                'Authorization': f'Basic {configuration.authorization}'
            },
        )
    )
    container_id = json.loads(response.read())['resource']['data'].split('/')[1]
    if 'win' in configuration.rid: suffix = 'zip'
    else: suffix = 'tar.gz'
    if 'servicing' in configuration.sdk_version or 'rtm' in configuration.sdk_version:
        version_number = configuration.sdk_version.split('-')[0]
        sdk_download_link = (
            f'https://dev.azure.com/dnceng/_apis/resources/Containers/{container_id}/'
            f'BlobArtifacts?itemPath=BlobArtifacts/dotnet-sdk-{version_number}-{configuration.rid}.{suffix}'
        )
    else:
        sdk_download_link = (
            f'https://dev.azure.com/dnceng/_apis/resources/Containers/{container_id}/'
            f'BlobArtifacts?itemPath=BlobArtifacts/dotnet-sdk-{configuration.sdk_version}-{configuration.rid}.{suffix}'
        )
    return sdk_download_link


def install_sdk(configuration: TestConfig):
    '''Install .net(core) sdk
    '''
    sdk_dir = os.environ['DOTNET_ROOT']
    if configuration.sdk_version[0] == '3':
        if 'win' in configuration.rid:
            req = request.urlopen('https://dot.net/v1/dotnet-install.ps1')
            with open(f'{configuration.test_bed}/dotnet-install.ps1', 'w+') as f:
                f.write(req.read().decode())
            rt_code = run_command_sync(
                ' '.join(
                    [
                        f'powershell.exe {configuration.test_bed}/dotnet-install.ps1',
                        f'-InstallDir {sdk_dir} -v {configuration.sdk_version}'
                    ]
                )
            )
        else:
            req = request.urlopen(
                'https://dotnet.microsoft.com/download/dotnet-core/scripts/v1/dotnet-install.sh'
            )
            with open(f'{configuration.test_bed}/dotnet-install.sh', 'w+') as f:
                f.write(req.read().decode())
            run_command_sync(f'chmod +x {configuration.test_bed}/dotnet-install.sh')
            rt_code = run_command_sync(
                ' '.join(
                    [
                        f'/bin/bash {configuration.test_bed}/dotnet-install.sh',
                        f'-InstallDir {sdk_dir} -v {configuration.sdk_version}'
                    ]
                )
            )
        if rt_code != 0:
            print(f'fail to install .net SDK {configuration.sdk_version}')
            exit(-1)
    else:
        sdk_download_link = get_sdk_download_link(configuration)

        compressed_file_path = os.path.join(
            configuration.test_bed,
            os.path.basename(sdk_download_link)
        )

        BUFFERSIZE = 64*1024*1024
        print(f'****** download sdk: {configuration.sdk_version} from Azure ******')
        try:
            response = request.urlopen(
                request.Request(
                    sdk_download_link,
                    headers={
                        'Authorization': f'Basic {configuration.authorization}'
                    },
                )
            )
            with open(compressed_file_path, 'wb+') as fs:
                while True:
                    buffer = response.read(BUFFERSIZE)
                    if buffer == b'' or len(buffer) == 0: break
                    fs.write(buffer)
        except Exception as e:
            print(f'fail to download package from Azure: {e}')
            if os.path.exists(compressed_file_path): os.remove(compressed_file_path)
            sys.exit(-1)

        print(f'****** decompress downloaded sdk package ******')
        decompressed_file_path = os.path.join(
            configuration.test_bed,
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
            print(f'fail to decompress downloaded package: {e}')
            if os.path.exists(decompressed_file_path): os.remove(decompressed_file_path)
            sys.exit(-1)
        finally:
            os.remove(compressed_file_path)

        print(f'****** extract decompressed package ******')
        try:
            if not os.path.exists(sdk_dir): os.makedirs(sdk_dir)
            if 'win' in configuration.rid:
                import zipfile
                with zipfile.ZipFile(decompressed_file_path, 'r') as zip_ref:
                    zip_ref.extractall(sdk_dir)
            else:
                import tarfile
                with tarfile.open(decompressed_file_path, 'r') as tar_ref:
                    tar_ref.extractall(sdk_dir)
        except Exception as e:
            print(f'fail to extract file: {e}')
            sys.exit(-1)
        finally:
            os.remove(decompressed_file_path)
