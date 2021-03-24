# coding=utf-8

import os
import json

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

    # establish connection
    try:
        connection = pika.BlockingConnection(
            pika.URLParameters(
                f'amqp://{user}:{password}@{ip}:{port}/{vhost}'
            )
        )
        channel = connection.channel()
    except Exception as e:
        message = f'fail to establish connection, Exception info: {e}'
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
        connection.close()
        return

    for runner in runner_list:
        queue_name = runner['name']
        try:
            while True:
                res = channel.queue_declare(queue=queue_name)
                if res.method.message_count == 0: 
                    print(f'queue `{queue_name}` is empty.')
                    break
                method, properties, body = channel.basic_get(
                    queue_name,
                    True
                )
                assign_task(json.loads(body.decode('utf-8')), runner)
        except Exception as e:
            message = f'fail to retrieve tasks, Exception info: {e}'
            print(message)
            connection.close()
            return
    connection.close()
    return


def assign_task(message: dict, runner: dict):
    '''Assign retrieved tasks to runners.

    Args:
        message - message retrieved from rabbitmq
        runner - info about the runner
    '''
    runner_type = runner['type']
    if runner_type == 'physic':
        run_task_on_device(message, runner)
    elif runner_type == 'container':
        run_task_on_docker(message, runner)
    else:
        raise(f'unknown runner type: {runner_type}')


def run_task_on_device(message: dict, runner: dict):
    '''Run task on physic machine.

    Args:
        message - message retrieved from rabbitmq
        runner - info about the runner
    '''
    pass


def run_task_on_docker(message: dict, runner: dict):
    '''Run task on container.

    Args:
        message - message retrieved from rabbitmq
        runner - info about the runner
    '''
    pass
