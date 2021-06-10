# coding=utf-8

import os
import configparser


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


class ProxyServerConf:
    def __init__(self, ini_file_path) -> None:
        config = configparser.ConfigParser()
        config.read(ini_file_path)
        self.host = config['connection'].get('host')
        self.port = config['connection'].getint('port')
