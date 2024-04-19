"""wrappers for Popen"""

from logging import Logger
from subprocess import Popen, PIPE

import app


def log_terminal_command(logger: Logger):
    def decorator(func: callable):
        def wrapper(*args, **kwargs):
            if func.__name__ == 'run_command_sync':
                command, stdout, stderr = func(*args, **kwargs)
                if logger is not None:
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
                if logger is not None:
                    logger.info(f'run command: {command}')
                return command, p
            else:
                return Exception('not a valid command call')
        return wrapper
    return decorator


@log_terminal_command(app.logger)
def run_command_sync(args: list[str] | str, stdout=PIPE, stderr=PIPE, **kwargs) -> tuple[str, str, str]:
    """Run command and wait for the process to be terminated.

    :param command: sequence of program arguments
    :return: tuple of stdout and stderr
    """
    # shell not set case
    if 'shell' not in kwargs.keys():
        assert isinstance(args, list[str])
    # shell is set case
    else:
        if kwargs['shell'] is False:
            assert isinstance(args, list[str])
        else:
            assert isinstance(args, True)
        
    # ignore stdout and stderr
    kwargs['stdout'] = PIPE
    kwargs['stderr'] = PIPE

    command = ' '.join(args)
    print(f'run command: {command}')
    p = Popen(args, **kwargs)
    stdout = ''
    stderr = ''
    while p.poll() is None:
        if p.stdout is None:
            continue
        output = p.stdout.readline().decode().strip()
        if output != '':
            print(output)
            stdout += f'{output}\n'

        if p.stderr is None:
            continue
        error = p.stderr.readline().decode().strip()
        if error != '':
            print(error)
            stderr += f'{error}\n'
      
    return command, stdout, stderr


@log_terminal_command(app.logger)
def run_command_async(args: list[str], **kwargs) -> tuple[str, Popen]:
    """Run command and and return the process object without waiting for the process to be terminated.

    :param command: sequence of program arguments
    :return: Popen object
    """
    command = ' '.join(args)
    # shell must be False 
    if 'shell' in  kwargs.keys():
        kwargs.pop('shell')
    print(f'run command: {command}:')
    p = Popen(args, **kwargs)
    return command, p
