# coding=utf-8

import os
import logging
from subprocess import PIPE, Popen


logging.root.setLevel(logging.NOTSET)


def run_command_sync(command, logger, stdin=None, 
    stdout=PIPE, stderr=PIPE, cwd=None)->int:
    '''Run command and wait for return.
    
    '''
    args = command.split(' ')
    logger.info(f'run command: {command}')

    try:
        p = Popen(args, stdin=stdin,
            stdout=stdout, stderr=stderr, cwd=cwd)
        outs, errs = p.communicate()
        outs = outs.decode()
        errs = errs.decode()

        logger.info(outs)
        if errs != '': logger.error(errs)
        return p.returncode
    except Exception as e:
        logger.error(f'fail to run command: {e}')
        return -1


def run_command_async(command, logger, 
    stdin=None, stdout=None, stderr=None, cwd=None)->Popen:
    '''Run command without waiting for return.
    
    '''
    args = command.split(' ')
    logger.info(f'run command: {command}')
    p = Popen(args, stdin=stdin, 
        stdout=stdout, stderr=stderr, cwd=cwd)
    return p


def create_logger(logger_name: str, logger_file_path: os.PathLike) -> logging.Logger:
    """Create a logger objectm which print message to console and file in the same time.

    """
    logger = logging.getLogger(logger_name)

    FILE_LOG_FORMAT = '\n%(module)s/%(filename)s/%(funcName)s - %(levelname)s\n%(message)s'
    file_log_handler = logging.FileHandler(filename=logger_file_path)
    file_log_handler.setFormatter(logging.Formatter(FILE_LOG_FORMAT))
    file_log_handler.setLevel(logging.DEBUG)

    CONSOLE_LOG_FORMAT = '\n%(message)s'
    console_log_handler = logging.StreamHandler()
    console_log_handler.setFormatter(logging.Formatter(CONSOLE_LOG_FORMAT))
    console_log_handler.setLevel(logging.INFO)

    logger.addHandler(console_log_handler)
    logger.addHandler(file_log_handler)

    return logger
