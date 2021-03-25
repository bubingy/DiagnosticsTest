# coding=utf-8

import os
import json
import shutil
from subprocess import Popen, PIPE

import pika

from utils import DictFromFile


def retrieve_task():
    '''Retrieve tasks from rabbitmq.
    '''
    # establish connection to rabbitmq
    try:
        connection_info = DictFromFile(
            os.path.join(
                os.path.dirname(os.path.abspath(__file__)),
                'conf',
                'connection.json'
            )
        ).content

        user = connection_info['user']
        password = connection_info['password']
        ip = connection_info['ip']
        port = connection_info['port']
        vhost = connection_info['vhost']
    except Exception as e:
        message = f'fail to load connection.json, Exception info: {e}'
        print(message)
        return

    # retrieve data
    try:
        runner_list = DictFromFile(
            os.path.join(
                os.path.dirname(os.path.abspath(__file__)),
                'conf',
                'runners.json'
            )
        ).content
    except Exception as e:
        message = f'fail to load runners.json, Exception info: {e}'
        print(message)
        return

    for runner in runner_list:
        queue_name = runner['queue']
        while True:
            try:
                connection = pika.BlockingConnection(
                    pika.URLParameters(
                        f'amqp://{user}:{password}@{ip}:{port}/{vhost}'
                    )
                )
                channel = connection.channel()
                res = channel.queue_declare(queue=queue_name)
                if res.method.message_count == 0: 
                    print(f'queue `{queue_name}` is empty.')
                    break
                method, properties, body = channel.basic_get(
                    queue_name,
                    True
                )
                connection.close()
                assign_task(json.loads(body.decode('utf-8')), runner)
            except Exception as e:
                message = f'fail to retrieve tasks, Exception info: {e}'
                print(message)
                return
    return


def assign_task(message: dict, runner: dict):
    '''Assign retrieved tasks to runners.

    Args:
        message - message retrieved from rabbitmq
        runner - info about the runner
    '''
    test_config = dict()
    test_config['Platform'] = dict()
    test_config['Platform']['RID'] = runner['queue']
    debugger_map = DictFromFile(
        os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            'conf',
            'DebuggerMap.json'
        )
    ).content
    test_config['Platform']['Debugger'] = debugger_map[message['OS']]
    test_config['SDK'] = dict()
    test_config['SDK']['Version'] = message['SDK']
    test_config['Tool'] = dict()
    test_config['Tool']['Version'] = message['Tool_Info']['version']
    test_config['Tool']['Commit'] = message['Tool_Info']['commit']
    test_config['Tool']['Feed'] = 'https://pkgs.dev.azure.com/dnceng/public/_packaging/dotnet-tools/nuget/v3/index.json'
    test_config['Test'] = dict()
    test_config['Test']['TestBed'] = runner['testbed']
    if message['SDK'][0] == '3':
        test_config['Test']['RunBenchmarks'] = 'true'
    else:
        test_config['Test']['RunBenchmarks'] = 'false'

    runner_type = runner['type']
    if runner_type == 'physic':
        run_task_on_device(test_config, runner)
    elif runner_type == 'container':
        run_task_on_docker(test_config, runner)
    else:
        raise(f'unknown runner type: {runner_type}')


def run_task_on_device(config: dict, runner: dict):
    '''Run task on physic machine.

    Args:
        config - test configuration
        runner - info about the runner
    '''
    automation_scripts_template = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        'AutomationScripts'
    )
    shutil.copy(automation_scripts_template, runner['testbed'])
    automation_scripts_dir = os.path.join(
        runner['testbed'],
        'AutomationScripts'
    )
    with open(os.path.join(automation_scripts_dir, 'config.json'), 'w') as f:
        json.dump(config, f)

    # run test
    if 'win' in runner['queue']:
        python_intepreter = 'python'
    else:
        python_intepreter = 'python3'
    start_script = os.path.join(automation_scripts_dir, 'run_test.py')
    command = f'{python_intepreter} {start_script}'
    process = Popen(command.split(' '), stdout=PIPE, stderr=PIPE)
    process.communicate()


def run_task_on_docker(config: dict, runner: dict):
    '''Run task on container.

    Args:
        config - test configuration
        runner - info about the runner
    '''
    automation_scripts_template = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        'AutomationScripts'
    )
    shutil.copy(automation_scripts_template, runner['testbed'])
    automation_scripts_dir = os.path.join(
        runner['testbed'],
        'AutomationScripts'
    )
    with open(os.path.join(automation_scripts_dir, 'config.json'), 'w') as f:
        json.dump(config, f)

    # run test
    start_script = os.path.join(automation_scripts_dir, 'run_test.py')
    docker_name = runner['name']
    command = (
        f'docker exec -ti {docker_name} '
        f'/bin/bash python3 {start_script}'
    ) # TODO
    process = Popen(command.split(' '), stdout=PIPE, stderr=PIPE)
    process.communicate()
