# coding=utf-8

import os
import json
import zipfile
import tempfile

from urllib import request
from xml.etree import ElementTree as ET


def get_latest_acceptable_build(definition_id: int,
                                authorization: str,
                                branch_name: str='main') -> dict:
    '''Get latest acceptable build in dotnet-diagnostics.

    An `Acceptable build` refers to 'succeeded' build or
        'partiallySucceeded' build.

    :param definition_id: definition id.
    :param authorization: authorization string.
    :return: the latest successful build or partially successful build.
    '''
    url = (
        'https://dev.azure.com/dnceng/internal/_apis/build/builds?'
        f'definitions={definition_id}'
        f'&branchName=refs/heads/{branch_name}'
        f'&reasonFilter=schedule,batchedCI'
        f'&resultFilter=succeeded,partiallySucceeded'
        '&queryOrder=finishTimeDescending'
        '&$top=1'
        '&api-version=6.1-preview.6'
    )
    response = request.urlopen(
        request.Request(
            url,
            headers={
                'Authorization': f'Basic {authorization}'
            }   
        )
    )
    response_content = response.read().decode('utf-8')
    build = json.loads(response_content)['value'][0]
    return build


def get_artifact(build_id: str, authorization: str, artifact_name : str='AssetManifests') -> dict:
    '''Get PackageArtifacts according to the given `build`.

    :param build: build information in json format.
    :param authorization: authorization string.
    :return: artifact information of build.
    '''
    url = (
        'https://dev.azure.com/dnceng/internal/_apis/'
        f'build/builds/{build_id}/artifacts?'
        f'artifactName={artifact_name}&api-version=6.1-preview.5'
    )
    response = request.urlopen(
        request.Request(
            url,
            headers={
                'Authorization': f'Basic {authorization}'
            }
        )
    )
    artifact = json.loads(response.read().decode())
    return artifact


def get_artifact_version(artifact: dict, authorization: str) -> str:
    '''Get tool's version according to the given `artifact`.

    :param artifact: artifact information in json format.
    :param authorization: authorization string.
    :return: version of artifacts.
    '''
    url = artifact['resource']['downloadUrl']
    response = request.urlopen(
        request.Request(
            url,
            headers={
                'Authorization': f'Basic {authorization}'
            }
        )
    )
    with tempfile.TemporaryDirectory() as tempdir:
        # download AssetManifests.zip
        file_path = os.path.join(tempdir, 'AssetManifests.zip')
        with open(file_path, 'wb+') as out:
            while True:
                buffer = response.read(4096)
                if not buffer: break
                out.write(buffer)
        # extract zip
        with zipfile.ZipFile(file_path, 'r') as zip_ref:
            zip_ref.extractall(tempdir)

        version = ''
        for file_name in os.listdir(os.path.join(tempdir, 'AssetManifests')):
            if file_name == 'Windows_NT-AnyCPU.xml':
                tree = ET.parse(
                    os.path.join(tempdir, 'AssetManifests', file_name)
                )
                root = tree.getroot()
                try:
                    version = root.findall(
                        '''.//Package[@Id='dotnet-counters']'''
                    )[0].attrib['Version']
                except Exception:
                    pass

                try:
                    version = root.findall(
                        '''.//Package[@Id='VS.Redist.Common.NetCore.SdkPlaceholder.x64']'''
                    )[0].attrib['Version']
                except Exception:
                    pass

            if file_name == 'Windows_NT-Windows_NT Build_Release_x64-AnyCPU.xml':
                tree = ET.parse(
                    os.path.join(tempdir, 'AssetManifests', file_name)
                )
                root = tree.getroot()
                version = root.findall(
                    '''.//Package[@Id='VS.Redist.Common.NetCore.SdkPlaceholder.x64']'''
                )[0].attrib['Version']

            if version != '': break
        return version
            