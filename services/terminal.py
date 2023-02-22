from subprocess import Popen


def run_command_sync(command, **kwargs)->tuple:
    args = command.split(' ')
    try:
        p = Popen(args, **kwargs)
        outs, errs = p.communicate()
        outs = outs.decode()
        errs = errs.decode()
    except Exception as e:
        outs, errs = '', e
    return outs, errs
    

def run_command_async(command: str, **kwargs)->Popen:
    '''Run command without waiting for return.
    
    '''
    args = command.split(' ')
    p = Popen(args, **kwargs)
    return p