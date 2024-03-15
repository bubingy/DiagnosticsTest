"""wrappers for Popen"""

from subprocess import Popen, PIPE


def run_command_sync(args: list[str], stdout=PIPE, stderr=PIPE, **kwargs) -> tuple:
    """Run command and wait for the process to be terminated.

    :param command: sequence of program arguments
    :return: tuple of stdout and stderr
    """
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

    return stdout, stderr


def run_command_async(command: list[str], **kwargs) -> Popen:
    """Run command and and return the process object without waiting for the process to be terminated.

    :param command: sequence of program arguments
    :return: Popen object
    """
    p = Popen(command, kwargs)
    return p
