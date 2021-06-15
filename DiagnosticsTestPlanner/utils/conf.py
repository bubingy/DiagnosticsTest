# coding=utf-8

import os
import base64
import configparser
from typing import Any

import redis


def load_json(file_path: os.PathLike) -> Any:
    import json
    content = None
    with open(file_path, 'r') as reader:
        content = reader.read()
    content = json.loads(content)
    return content


class WeeklyTestConf:
    '''Load weekly test configuration.
    
    '''
    def __init__(self, ini_file_path: os.PathLike) -> None:
        test_conf = configparser.ConfigParser()
        test_conf.read(ini_file_path)
        self.major_version_list = test_conf['Branch']['major'].split('\n')
        self.major_version_list.remove('')
        self.tool_feed = test_conf['Tool']['feed']


class ReleaseTestConf:
    '''Load release test configuration.

    '''
    def __init__(self, ini_file_path: os.PathLike) -> None:
        test_conf = configparser.ConfigParser()
        test_conf.read(ini_file_path)
        self.sdk_list = test_conf['SDK']['version'].split('\n')
        self.sdk_list.remove('')
        self.tool_version = test_conf['Tool']['version']
        self.tool_feed = test_conf['Tool']['feed']
        self.os_list = test_conf['Scenarios']['os'].split('\n')
        self.os_list.remove('')


class AzureQueryConf:
    '''Load Azure pipeline info.

    '''
    def __init__(self, ini_file_path: os.PathLike) -> None:
        pipe_conf = configparser.ConfigParser()
        pipe_conf.read(ini_file_path)
        self.pat = pipe_conf['Auth']['pat']
        self.definition_id_map = dict()
        for pipeline_name in pipe_conf['Pipeline'].keys():
            self.definition_id_map[pipeline_name] = \
                pipe_conf['Pipeline'][pipeline_name]
        self.authorization = str(
            base64.b64encode(bytes(f':{self.pat}', 'ascii')),
            'ascii'
        )


class RedisConnection:
    def __init__(self, ini_file_path) -> None:
        config = configparser.ConfigParser()
        config.read(ini_file_path)
        self.host = config['Redis'].get('host')
        self.port = config['Redis'].getint('port')

        self.runner_table_conn = redis.Redis(
            self.host,
            self.port,
            0
        )
        self.diagnostics_task_table_conn = redis.Redis(
            self.host,
            self.port,
            1
        )