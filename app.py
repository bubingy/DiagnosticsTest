
import os
import logging
 

# App logger
logging.root.setLevel(logging.NOTSET)
class AppLogger(logging.Logger):
    def __init__(self, name: str, logger_file_path: os.PathLike, level: int = logging.INFO) -> None:
        super().__init__(name, level)

        FILE_LOG_FORMAT = '%(levelname)s> %(module)s.%(funcName)s:\n%(message)s'
        file_log_handler = logging.FileHandler(filename=logger_file_path)
        file_log_handler.setFormatter(logging.Formatter(FILE_LOG_FORMAT))
        file_log_handler.setLevel(logging.DEBUG)
        self.addHandler(file_log_handler)


def function_monitor(pre_run_msg: str=None, post_run_msg: str=None):
    def decorator(func: callable):
        def wrapper(*args, **kwargs):
            # if there is exception in args, return exception directly
            for arg in args:
                if isinstance(arg, Exception):
                    return arg
                
            # print or log pre-run message
            if pre_run_msg is not None:
                print(pre_run_msg)
                if logger is not None:
                    logger.info(pre_run_msg)

            # run the function
            result = func(*args, **kwargs)
            if isinstance(result, Exception):
                if logger is not None:
                    logger.error(f'fail to run function {func.__name__}: {result}')
                else:
                    print(f'fail to run function {func.__name__}: {result}')

            # print or log post-run message
            if post_run_msg is not None:
                print(post_run_msg)
                if logger is not None:
                    logger.info(post_run_msg)
                    
            return result
        return wrapper
    return decorator


# global instances
script_root = os.path.dirname(__file__)
logger: AppLogger = None