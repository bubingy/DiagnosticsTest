# coding=utf-8

import json
from urllib import request


def list_branches(owner: str, repo: str) -> list:
    '''List all branches of .NET installer
    
    :param owner: name of owner.
    :param repo: name of repo.
    :return: list of branches.
    '''
    url = f'https://api.github.com/repos/{owner}/{repo}/branches?per_page=100'
    response_content = request.urlopen(url).read().decode('utf-8')
    return json.loads(response_content)


def get_pr_info(owner: str, repo: str, commit_id: str) -> dict:
    '''Get pull number of given commit id.

    :param owner: name of owner.
    :param repo: name of repo.
    :commit_id: commit id.
    return: a dict object in following format
        {
            'pull_number': pull number,
            'pull_html_url': pull link
        }
    '''
    page = 0
    while True:
        page += 1
        url = (
            f'https://api.github.com/repos/{owner}/{repo}/pulls?'
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
