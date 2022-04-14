import os
import logging


logging.root.setLevel(logging.NOTSET)

class ScriptLogger(logging.Logger):
    def __init__(self, name: str, logger_file_path: os.PathLike, level = logging.INFO) -> None:
        super().__init__(name, level)

        FILE_LOG_FORMAT = '%(levelname)s> %(module)s.%(funcName)s:\n%(message)s'
        file_log_handler = logging.FileHandler(filename=logger_file_path)
        file_log_handler.setFormatter(logging.Formatter(FILE_LOG_FORMAT))
        file_log_handler.setLevel(logging.DEBUG)

        CONSOLE_LOG_FORMAT = '%(message)s'
        console_log_handler = logging.StreamHandler()
        console_log_handler.setFormatter(logging.Formatter(CONSOLE_LOG_FORMAT))
        console_log_handler.setLevel(logging.INFO)

        self.addHandler(file_log_handler)
        self.addHandler(console_log_handler)