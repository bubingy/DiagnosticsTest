# coding=utf-8

import os
import shutil
from subprocess import PIPE, Popen

from config import configuration


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


def clean():
    if 'win' in configuration.rid: home_path = os.environ['USERPROFILE']
    else: home_path = os.environ['HOME']

    to_be_removed = [
        os.path.join(home_path, '.aspnet'),
        os.path.join(home_path, '.dotnet'),
        os.path.join(home_path, '.nuget'),
        os.path.join(home_path, '.templateengine'),
        os.path.join(home_path, '.lldb'),
        os.path.join(home_path, '.lldbinit'),
        os.path.join(home_path, '.local'),
        os.path.join(configuration.test_bed, '.dotnet-test')
    ]

    for f in to_be_removed:
        if not os.path.exists(f): continue
        if os.path.isdir(f): shutil.rmtree(f)
        else: os.remove(f)


class Result:
    '''This class is used to store result.
    '''
    def __init__(self, code, message, data):
        self.code = code
        self.message = message
        self.data = data