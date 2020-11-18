# coding=utf-8

from subprocess import PIPE, Popen

def run_command_sync(command, log_path=None, bufsize=-1, 
    stdin=None, stdout=PIPE, stderr=PIPE, cwd=None)->int:
    '''Run command and wait for return.
    
    '''
    args = command.split(' ')
    print(command)
    p = Popen(args, bufsize=-1, 
        stdin=stdin, stdout=stdout, stderr=stderr, cwd=cwd)
    outs, errs = p.communicate()
    outs = outs.decode()
    errs = errs.decode()
    if log_path is not None:
        with open(log_path, 'a+') as log:
            log.write(f'{command}\n')
            log.write(f'{outs}\n')
            log.write(f'{errs}\n')
    print(outs)
    print(errs)
    return p.returncode


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


class Result:
    '''This class is used to store result.
    '''
    def __init__(self, code, message, data):
        self.code = code
        self.message = message
        self.data = data