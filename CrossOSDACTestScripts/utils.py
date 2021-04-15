'''Utils
'''
#  coding=utf-8

from subprocess import PIPE, Popen

def run_command_sync(command, log_path=None, env=None,
    stdin=None, stdout=PIPE, stderr=PIPE, cwd=None)->int:
    '''Run command and wait for return.

    '''
    args = command.split(' ')
    print(command)
    if log_path is not None:
        with open(log_path, 'a+') as log:
            log.write(f'{command}\n')
    try:
        process = Popen(args, bufsize=-1, env=env,
            stdin=stdin, stdout=stdout, stderr=stderr, cwd=cwd)
        outs, errs = process.communicate()
        outs = outs.decode()
        errs = errs.decode()
        if log_path is not None:
            with open(log_path, 'a+') as log:
                log.write(f'{outs}\n')
                log.write(f'{errs}\n')
        print(outs)
        print(errs)
        return process.returncode
    except Exception as exception:
        if log_path is not None:
            with open(log_path, 'a+') as log:
                log.write(f'{exception}\n')
        print(exception)
        return -1


def run_command_async(command, log_path=None,
    stdin=None, stdout=None, stderr=None, cwd=None)->Popen:
    '''Run command without waiting for return.

    '''
    args = command.split(' ')
    print(command)
    if log_path is not None:
        with open(log_path, 'a+') as log:
            log.write(f'{command}\n')
    return Popen(args, stdin=stdin,
        stdout=stdout, stderr=stderr, cwd=cwd)


class Result:
    '''This class is used to store result.
    '''
    def __init__(self, code, message, data):
        self.code = code
        self.message = message
        self.data = data
