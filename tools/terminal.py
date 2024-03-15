"""wrappers for Popen"""

from subprocess import Popen, PIPE

import app


@app.log_terminal_command()
def run_command_sync(args: list[str], stdout=PIPE, stderr=PIPE, **kwargs) -> tuple[str, str, str]:
    """Run command and wait for the process to be terminated.

    :param command: sequence of program arguments
    :return: tuple of stdout and stderr
    """
    # ignore stdout and stderr
    kwargs.pop('stdout')
    kwargs.pop('stderr')

    command = ' '.join(args)
    print(f'run command: {command}')

    p = Popen(args, kwargs)
    stdout = ''
    stderr = ''
    while p.poll() is None:
        output = p.stdout.readline().decode().strip()
        if output != '':
            print(output)
            stdout += f'{output}\n'

        error = p.stderr.readline().decode().strip()
        if error != '':
            print(error)
            stderr += f'{error}\n'

    return command, stdout, stderr


@app.log_terminal_command()
def run_command_async(args: list[str], **kwargs) -> tuple[str, Popen]:
    """Run command and and return the process object without waiting for the process to be terminated.

    :param command: sequence of program arguments
    :return: Popen object
    """
    command = ' '.join(args)
    print(f'run command: {command}:')
    p = Popen(args, kwargs)
    return command, p
