
import os
import logging
 

# App logger
logging.root.setLevel(logging.NOTSET)
class AppLogger(logging.Logger):
    def __init__(self, name: str, logger_file_path: os.PathLike = None, level: int = logging.INFO) -> None:
        super().__init__(name, level)

        CONSOLE_LOG_FORMAT = '%(message)s'
        console_log_handler = logging.StreamHandler()
        console_log_handler.setFormatter(logging.Formatter(CONSOLE_LOG_FORMAT))
        console_log_handler.setLevel(logging.INFO)
        self.addHandler(console_log_handler)

        if logger_file_path is not None:
            FILE_LOG_FORMAT = '%(levelname)s> %(module)s.%(funcName)s:\n%(message)s'
            file_log_handler = logging.FileHandler(filename=logger_file_path)
            file_log_handler.setFormatter(logging.Formatter(FILE_LOG_FORMAT))
            file_log_handler.setLevel(logging.DEBUG)
            self.addHandler(file_log_handler)


# global instances
logger: AppLogger = None   