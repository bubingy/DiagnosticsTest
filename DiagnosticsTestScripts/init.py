'''Install sdk and tools
'''

import os
import sys
import json
import gzip
import logging
from urllib import request

import config
from utils import run_command_sync


def get_sdk_download_link(configuration: config.TestConfig) -> str:
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
    return (
        f'https://dev.azure.com/dnceng/_apis/resources/Containers/{container_id}/'
        f'BlobArtifacts?itemPath=BlobArtifacts/dotnet-sdk-{configuration.sdk_version}-{configuration.rid}.{suffix}'
    )


def install_sdk(configuration: config.TestConfig, logger: logging.Logger):
    '''Install .net(core) sdk
    '''
    logger.info(f'****** install .net sdk ******')
    
    sdk_download_link = get_sdk_download_link(configuration)

    compressed_file_path = os.path.join(
        configuration.test_bed,
        os.path.basename(sdk_download_link)
    )

    BUFFERSIZE = 64*1024*1024
    logger.info(f'****** download sdk package from Azure ******')
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
        logger.error(f'fail to download package from Azure: {e}')
        if os.path.exists(compressed_file_path): os.remove(compressed_file_path)
        sys.exit(-1)

    logger.info(f'****** decompress downloaded sdk package ******')
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
        logger.error(f'fail to decompress downloaded package: {e}')
        if os.path.exists(decompressed_file_path): os.remove(decompressed_file_path)
        sys.exit(-1)
    finally:
        os.remove(compressed_file_path)

    sdk_dir = os.environ['DOTNET_ROOT']
    logger.info(f'****** extract decompressed package ******')
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
        logger.error(f'fail to extract file: {e}')
        sys.exit(-1)
    finally:
        os.remove(decompressed_file_path)

    logger.info(f'****** install sdk finished ******')


def install_tools(configuration: config.TestConfig, logger: logging.Logger):
    '''Install diagnostics
    '''
    logger.info(f'****** install diagnostics tools ******')
    tools = [
        'dotnet-counters',
        'dotnet-dump',
        'dotnet-gcdump',
        'dotnet-sos',
        'dotnet-trace'
    ]
    for tool in tools:
        command = ' '.join(
            [
                f'dotnet tool install {tool}',
                f'--tool-path {configuration.tool_root}',
                f'--version {configuration.tool_version}',
                f'--add-source {configuration.tool_feed}'
            ]
        )
        rt_code = run_command_sync(command, logger)
        if rt_code != 0:
            logger.error(f'fail to install tool: {tool}!')
            logger.info(f'****** install diagnostics tools finished ******')
            sys.exit(-1)
    logger.info(f'****** install diagnostics tools finished ******')
