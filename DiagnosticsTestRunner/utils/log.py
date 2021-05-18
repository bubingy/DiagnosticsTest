# coding=utf-8

import os
import logging
from typing import Any

logging.root.setLevel(logging.NOTSET)


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