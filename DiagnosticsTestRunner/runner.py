# coding=utf-8

import os
import time
import json
import shutil
from datetime import datetime
from subprocess import Popen

import pika
import schedule

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
                if res.method.message_count == 0: break
                
                print(f'retrieving message from {queue_name}...')
                method, properties, body = channel.basic_get(
                    queue_name,
                    True # turn to True before deploying.
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
    test_config = message.copy()
    test_config['Tool_Info']['feed'] = 'https://pkgs.dev.azure.com/dnceng/public/_packaging/dotnet-tools/nuget/v3/index.json'
    test_config['Test'] = dict()
    # TODO: make it readable.
    test_config['Test']['TestBed'] = os.path.join(
        runner['mount']['container'],
        '_'.join(
            [
                os.path.basename(runner['testbed']),
                test_config['OS'],
                runner['queue'],
                datetime.now().strftime('%Y%m%d%H%M%S')
            ]
        )  
    )

    if message['SDK'][0] == '3':
        test_config['Test']['RunBenchmarks'] = 'true'
    else:
        test_config['Test']['RunBenchmarks'] = 'false'

    runner_type = runner['type']
    runner_name = runner['name']
    if runner_type == 'physic':
        print(f'running task on device {runner_name}...')
        run_task_on_device(test_config, runner)
    elif runner_type == 'container':
        print(f'running task on container {runner_name}...')
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
    if not os.path.exists(runner['testbed']):
        os.mkdir(runner['testbed'])
    automation_scripts_dir = os.path.join(
        runner['testbed'],
        'AutomationScripts'
    )
    if os.path.exists(automation_scripts_dir):
        os.removedirs(automation_scripts_dir)
    shutil.copytree(automation_scripts_template, automation_scripts_dir)
    with open(os.path.join(automation_scripts_dir, 'config.json'), 'w') as f:
        json.dump(config, f)

    # run test
    if 'win' in runner['queue']:
        python_intepreter = 'python'
    else:
        python_intepreter = 'python3'
    start_script = os.path.join(automation_scripts_dir, 'run_test.py')
    command = f'{python_intepreter} {start_script}'
    print(f'exec {command}')
    process = Popen(command.split(' '))
    process.communicate()
    print('task completed!')


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
    if not os.path.exists(runner['testbed']):
        os.mkdir(runner['testbed'])  
    automation_scripts_dir = os.path.join(
        runner['testbed'],
        'AutomationScripts'
    )
    if os.path.exists(automation_scripts_dir) is True:
        os.removedirs(automation_scripts_dir)
    shutil.copytree(automation_scripts_template, automation_scripts_dir)
    with open(os.path.join(automation_scripts_dir, 'config.json'), 'w') as f:
        json.dump(config, f)

    # run test
    docker_name = runner['name']
    start_up_script = os.path.join(
        config['Test']['TestBed'],
        'AutomationScripts',
        'run_test.py'
    )
    command = (
        f'docker exec -ti {docker_name} '
        f'python3 {start_up_script}'
    )
    print(f'exec {command}')
    process = Popen(command.split(' '))
    process.communicate()
    print('task completed!')


if __name__ == "__main__":
    schedule.every().minute.do(retrieve_task)
    while True:
        schedule.run_pending()
        time.sleep(10)