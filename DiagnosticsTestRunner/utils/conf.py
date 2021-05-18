# coding=utf-8

import os
import base64
import configparser


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

