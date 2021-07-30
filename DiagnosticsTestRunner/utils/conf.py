# coding=utf-8

import os
import configparser

from utils.RedisTCPClient import RedisTCPClient


class RunnerConf:
    '''Load configuration for runner.

    '''
    def __init__(self, ini_file_path: os.PathLike) -> None:
        runner_conf = configparser.ConfigParser()
        runner_conf.read(ini_file_path)
        self.host_name = runner_conf['runner']['hostname']
        self.runner_name = runner_conf['runner']['runnername']
        self.output_folder = runner_conf['runner']['outputfolder']

        if not os.path.exists(self.output_folder):
            os.makedirs(self.output_folder)


class RedisClient(RedisTCPClient):
    '''Redis client.

    '''
    def __init__(self,
                 ini_file_path: os.PathLike,
                 buffer_size: int=4096,
                 coding='utf-8') -> None:
        redis_conf = configparser.ConfigParser()
        redis_conf.read(ini_file_path)
        host = redis_conf['redis']['hostname']
        port = redis_conf['redis']['port']
        super().__init__(host, port, buffer_size=buffer_size, coding=coding)
