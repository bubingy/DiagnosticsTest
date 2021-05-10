# coding=utf-8

import os
import logging
import configparser
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
        
        self.rabbitmq_url = (
            'amqp://'
            f'{self.username}:'
            f'{self.password}@'
            f'{self.ipaddr}:'
            f'{self.port}/'
            f'{self.vhost}'    
        )


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
