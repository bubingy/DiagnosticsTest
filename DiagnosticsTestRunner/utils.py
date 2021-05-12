# coding=utf-8

import os
import json
import base64
import logging
import configparser
from urllib import request
from typing import Any

logging.root.setLevel(logging.NOTSET)


class RunnerConfig:
    '''Read configuration from ini file.
    
    :param ini_file_path: path of ini file.
    :return: a configparser.ConfigParser object.
    '''
    def __init__(self, ini_file_path: os.PathLike) -> None:
        assert os.path.exists(ini_file_path)
        assert os.path.isfile(ini_file_path)

        config = configparser.ConfigParser()
        config.read(ini_file_path)

        for section in config.sections():
            for key in config[section].keys():
                self.__setattr__(key, config[section][key])
        
        self.base_url = f'http://{self.ipaddr}:{self.port}'
        auth_str = str(
            base64.b64encode(
                bytes(
                    f'{self.username}:{self.password}',
                    'ascii'
                )
            ),
            'ascii'
        )
        self.general_header = {
            'Authorization': f'Basic {auth_str}',
            'content-type':'application/json'
        }


class Logger(logging.Logger):
    '''A logger object.

    '''
    def __init__(self, 
                 name: str,
                 logger_file_path: os.PathLike,
                 level: Any=logging.NOTSET) -> None:
        super().__init__(name, level=level)

        FILE_LOG_FORMAT = '%(asctime)s %(module)s/%(filename)s/%(funcName)s - %(levelname)s - %(message)s'
        file_log_handler = logging.FileHandler(filename=logger_file_path)
        file_log_handler.setFormatter(logging.Formatter(FILE_LOG_FORMAT))
        file_log_handler.setLevel(logging.DEBUG)

        CONSOLE_LOG_FORMAT = '%(asctime)s - %(levelname)s - %(message)s'
        console_log_handler = logging.StreamHandler()
        console_log_handler.setFormatter(logging.Formatter(CONSOLE_LOG_FORMAT))
        console_log_handler.setLevel(logging.INFO)

        self.addHandler(console_log_handler)
        self.addHandler(file_log_handler)


def declare_queue(queue_name: str, connection_conf: RunnerConfig) -> int:
    data = {
        'auto_delete':'false',
        'durable':'false'
    }
    uri = f'/api/queues/{connection_conf.vhost}/{queue_name}'
    req = request.Request(
        f'{connection_conf.base_url}{uri}',
        headers=connection_conf.general_header,
        data=json.dumps(data).encode("utf-8"),
        method='PUT'
    )
    try:
        request.urlopen(req).read().decode('utf-8')
        return 0
    except Exception as e:
        print(f'fail to declare queue: {e}')
        return 1


def get_message(queue_name: str, connection_conf: RunnerConfig) -> str:
    data = {
        'count':1,
        'ackmode':'ack_requeue_false',
        'encoding':'auto'
    }
    uri = f'/api/queues/{connection_conf.vhost}/{queue_name}/get'
    req = request.Request(
        f'{connection_conf.base_url}{uri}',
        headers=connection_conf.general_header,
        data=json.dumps(data).encode("utf-8"),
        method='POST'
    )
    try:
        content = json.loads(
            request.urlopen(req).read().decode('utf-8')
        )[0]['payload']
    except Exception as e:
        print(f'fail to publish message: {e}')
        content = None
    return content


# if __name__ == '__main__':
