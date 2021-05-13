# coding=utf-8

import os
import base64
import logging
import configparser
from typing import Any

logging.root.setLevel(logging.NOTSET)


class RunnerConf:
    '''Load configuration for runner.

    '''
    def __init__(self, ini_file_path: os.PathLike) -> None:
        runner_conf = configparser.ConfigParser()
        runner_conf.read(ini_file_path)
        self.runner_name = runner_conf['runner']['runnername']
        self.output_dir = None

    def init(self):
        assert self.output_dir is not None
        if not os.path.exists(self.output_dir): os.makedirs(self.output_dir)


class MQConnectionConf:
    '''Load rabbitmq connection info.

    This class include following properties:
        username: username of rabbitmq.
        password: password.
        ipaddr: ip address of host where rabbitmq run.
        port: port number of rabbitmq-management-plugin.
        vhost: name of vhost.
        base_url: base url for http api.
        general_header: request header for general usage.
    '''
    def __init__(self, ini_file_path: os.PathLike) -> None:
        connection_conf = configparser.ConfigParser()
        connection_conf.read(ini_file_path)
        self.username = connection_conf['connection']['username']
        self.password = connection_conf['connection']['password']
        self.ipaddr = connection_conf['connection']['ipaddr']
        self.port = connection_conf['connection']['port']
        self.vhost = connection_conf['connection']['vhost']
        
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


# if __name__ == '__main__':
