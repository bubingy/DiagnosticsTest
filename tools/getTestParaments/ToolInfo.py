# coding=utf-8

import os
import json
import zipfile
import tempfile
from typing import Any
from urllib import request


def load_json(file_path: os.PathLike) -> Any:
    import json
    content = None
    with open(file_path, 'r') as reader:
        content = reader.read()
    content = json.loads(content)
    return content


class ToolInfo:
    def __init__(self):
        self.configuration = load_json(
            os.path.join(
                os.path.dirname(os.path.abspath(__file__)),
                'configuration.json'
            )
        )

        self.build = self.get_latest_acceptable_build()
        self.artifact = self.get_artifact(self.build)
        self.tool_version = self.get_tool_version(self.artifact)
        self.pr_info = self.get_pr_info(self.build)

    def get_latest_acceptable_build(self) -> dict:
        '''Get latest acceptable build in dotnet-diagnostics.

        An `Acceptable build` refers to 'succeeded' build or
            'partiallySucceeded' build.

        Return: a dict object.
        '''

        results = self.configuration['results']

        acceptable_builds = []
        for result in results:
            url = (
                'https://dev.azure.com/dnceng/internal/_apis/build/builds?'
                'definitions=528'
                '&branchName=refs/heads/main'
                '&reasonFilter=batchedCI/schedule'
                f'&resultFilter={result}'
                '&queryOrder=finishTimeDescending'
                '&$top=1'
                '&api-version=6.1-preview.6'
            )
            response = request.urlopen(
                request.Request(
                    url,
                    headers={
                        'cookie': self.configuration['headers']['cookie']
                    },
                    
                )
            )
            build = json.loads(response.read().decode())['value'][0]
            acceptable_builds.append(build)

            if len(acceptable_builds) == 0:
                print('no acceptable builds available.')
                return None

            if len(acceptable_builds) == 1:
                return acceptable_builds[0]

            if acceptable_builds[0]['id'] > acceptable_builds[1]['id']:
                return acceptable_builds[0]
            else:
                return acceptable_builds[1]


    def get_artifact(self, build: dict) -> dict:
        '''Get PackageArtifacts according to the given `build`.

        Args:
            build - build information in json format.
        Return: a dict object.
        '''
        build_id = build['id']
        url = (
            'https://dev.azure.com/dnceng/internal/_apis/'
            f'build/builds/{build_id}/artifacts?'
            'artifactName=PackageArtifacts&api-version=6.1-preview.5'
        )
        response = request.urlopen(
            request.Request(
                url,
                headers={
                    'cookie': self.configuration['headers']['cookie']
                },
                
            )
        )
        artifact = json.loads(response.read().decode())
        return artifact


    def get_tool_version(self, artifact: dict) -> str:
        '''Get tool's version according to the given `artifact`.

        Args:
            artifact - artifact information in json format.
        Return: string.
        '''
        url = artifact['resource']['downloadUrl']
        response = request.urlopen(
            request.Request(
                url,
                headers={
                    'cookie': self.configuration['headers']['cookie']
                },
                
            )
        )
        with tempfile.TemporaryDirectory() as tempdir:
            # download PackageArtifacts.zip
            file_path = os.path.join(tempdir, 'PackageArtifacts.zip')
            with open(file_path, 'wb+') as out:
                while True:
                    buffer = response.read(4096)
                    if not buffer: break
                    out.write(buffer)
            # extract zip
            with zipfile.ZipFile(file_path, 'r') as zip_ref:
                zip_ref.extractall(tempdir)
            # get tool version
            for file_name in os.listdir(os.path.join(tempdir, 'PackageArtifacts')):
                if 'dotnet-counters' in file_name:
                    tool_version = file_name.replace('dotnet-counters.', '')
                    tool_version = tool_version.replace('.nupkg', '')
                    return tool_version


    def get_pr_info(self, build: dict) -> dict:
        '''Get pull number of given commit id.

        Args:
            build - build information in json format.
        return: a dict object in following format
            {
                'pull_number': pull number,
                'pull_html_url': pull link
            }
        '''
        commit_id = build['sourceVersion']
        page = 0
        while True:
            page += 1
            url = (
                'https://api.github.com/repos/dotnet/diagnostics/pulls?'
                'state=closed&'
                'per_page=100&'
                f'page={page}'
            )
            response = request.urlopen(
                request.Request(
                    url,
                    headers={
                        'Accept': 'application/vnd.github.cloak-preview+json'
                    }
                )
            )
            pulls = json.loads(response.read().decode())
            for pull in pulls:
                if pull['merge_commit_sha'] == commit_id:
                    pull_info = {
                        'pull': pull['number'],
                        'pull_html_url': pull['html_url'],
                        'commit': commit_id,
                        'commit_html_url': f'https://github.com/dotnet/diagnostics/commit/{commit_id}'
                    }
                    return pull_info
            if page >= 100:
                print(f'can\'t find the pull number with commit sha {commit_id}. Search it manualy.')
                return None