from subprocess import Popen, PIPE


def run_command_sync(command, stdin=None, stdout=PIPE, stderr=PIPE, cwd=None, **kwargs)->tuple:
    args = command.split(' ')
    try:
        p = Popen(args, stdin=stdin,
            stdout=stdout, stderr=stderr, cwd=cwd, **kwargs)
        outs, errs = p.communicate()
        outs = outs.decode()
        errs = errs.decode()
    except Exception as e:
        outs, errs = '', e
    return outs, errs
    

def run_command_async(command: str, stdin=None, stdout=None, stderr=None, cwd=None, **kwargs)->Popen:
    '''Run command without waiting for return.
    
    '''
    args = command.split(' ')
    p = Popen(args, stdin=stdin,
        stdout=stdout, stderr=stderr, cwd=cwd, **kwargs)
    return p