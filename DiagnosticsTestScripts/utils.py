# coding=utf-8

import os
from functools import wraps
from subprocess import PIPE, Popen
from typing import Callable


def run_command_sync(command, log_path=None, bufsize=-1, 
    stdin=None, stdout=PIPE, stderr=PIPE, cwd=None, silent=False)->int:
    '''Run command and wait for return.
    
    '''
    args = command.split(' ')
    print(command)
    if log_path is not None:
        with open(log_path, 'a+') as log:
            log.write(f'{command}\n')
    try:
        p = Popen(args, bufsize=-1, 
            stdin=stdin, stdout=stdout, stderr=stderr, cwd=cwd)
        outs, errs = p.communicate()
        outs = outs.decode()
        errs = errs.decode()
        if log_path is not None:
            with open(log_path, 'a+') as log:
                log.write(f'{outs}\n')
                log.write(f'{errs}\n')
        if not silent:
            print(outs)
            print(errs)
        return p.returncode
    except Exception as e:
        if log_path is not None:
            with open(log_path, 'a+') as log:
                log.write(f'{e}\n')
        if not silent: print(e)
        return -1


def run_command_async(command, log_path=None, bufsize=-1, 
    stdin=None, stdout=None, stderr=None, cwd=None)->Popen:
    '''Run command without waiting for return.
    
    '''
    args = command.split(' ')
    print(command)
    if log_path is not None:
        with open(log_path, 'a+') as log:
            log.write(f'{command}\n')
    p = Popen(args, bufsize=-1, stdin=stdin, 
        stdout=stdout, stderr=stderr, cwd=cwd)
    return p


def test_logger(log_path):
    def logging_decorator(func: Callable):
        @wraps(func)
        def decorated(*args, **kwargs):
            with open(log_path, 'a+') as fs:
                fs.write(f'****** run {func.__name__} ******\r\n')
            rt = func(*args, log_path=log_path, **kwargs)
            with open(log_path, 'a+') as fs:
                fs.write(f'****** completed ******\r\n')  
            return rt
        return decorated
    return logging_decorator


class Result:
    '''This class is used to store result.
    '''
    def __init__(self, code, message, data):
        self.code = code
        self.message = message
        self.data = data