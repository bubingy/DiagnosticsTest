
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


def log_terminal_command():
    def decorator(func: callable):
        def wrapper(*args, **kwargs):
            if func.__name__ == 'run_command_sync':
                command, stdout, stderr = func(*args, **kwargs)
                logger.info(
                    '\n'.join(
                        [
                            f'run command: {command}',
                            stdout,
                            stderr
                        ]
                    )
                )
                return command, stdout, stderr
            elif func.__name__ == 'run_command_async':
                command, p = func(*args, **kwargs)
                logger.info(f'run command: {command}')
                return command, p
            else:
                return Exception('not a valid command call')
        return wrapper
    return decorator


def log_function(pre_run_msg: str=None, post_run_msg: str=None):
    def decorator(func: callable):
        def wrapper(*args, **kwargs):
            # run the function
            if pre_run_msg is not None:
                logger.info(pre_run_msg)
            result = func(*args, **kwargs)
            if isinstance(result, Exception):
                logger.error(f'fail to run function {func.__name__}: {result}')
            if post_run_msg is not None:
                logger.info(post_run_msg)
            return result
        return wrapper
    return decorator


def check_function_input():
    def decorator(func:callable):
        def wrapper(*args, **kwargs):
            for arg in args:
                if isinstance(arg, Exception):
                    return arg

            return func(*args, **kwargs)
        return wrapper
    return decorator 


# global instances
logger: AppLogger = None