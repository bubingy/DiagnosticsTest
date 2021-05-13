# coding=utf-8

import os
import time
import json
import argparse
from urllib import request
from datetime import datetime

import global_var
import AutomationScripts
from utils import MQConnectionConf, RunnerConf, Logger


def declare_queue(queue_name: str, connection_conf: MQConnectionConf) -> int:
    '''Declare a queue.

    :param queue_name: name of queue.
    :param connection_conf: rabbitmq connection info.
    :return: 0 if successes, 1 if fails. 
    '''
    data = {
        'auto_delete':'false',
        'durable':'false'
    }
    uri = f'/api/queues/{connection_conf.vhost}/{queue_name}'
    req = request.Request(
        f'{connection_conf.base_url}{uri}',
        headers=connection_conf.general_header,
        data=json.dumps(data).encode("utf-8"),
        method='PUT'
    )
    try:
        request.urlopen(req).read().decode('utf-8')
        return 0
    except Exception as e:
        global_var.LOGGER.error(
            f'declare queue {queue_name} failed with exception: {e}.'
        )
        return 1


def get_queue_length(queue_name: str, connection_conf: MQConnectionConf) -> int:
    '''Get length of queue.
    
    :param queue_name: name of queue.
    :param connection_conf: rabbitmq connection info.
    :return: length of queue.
    '''
    uri = f'/api/queues/{connection_conf.vhost}/{queue_name}'
    req = request.Request(
        f'{connection_conf.base_url}{uri}',
        headers=connection_conf.general_header,
        method='GET'
    )
    try:
        content = json.loads(
            request.urlopen(req).read().decode('utf-8')
        )
        return content['messages']
    except Exception as e:
        global_var.LOGGER.error(
            f'get length of queue {queue_name} failed with exception: {e}.'
        )
        return -1


def get_message(queue_name: str, connection_conf: MQConnectionConf, requeue: bool=False) -> str:
    '''Retrieve a message from queue.

    :param queue_name: name of queue.
    :param connection_conf: rabbitmq connection info.
    :param requeue: whether to requeue the message. 
        False by default. if True, remove the message from the queue.
    :return: retrieved message. 
    '''
    if requeue: ackmode = 'ack_requeue_true'
    else: ackmode = 'ack_requeue_false'
    data = {
        'count':1,
        'ackmode':ackmode,
        'encoding':'auto'
    }
    uri = f'/api/queues/{connection_conf.vhost}/{queue_name}/get'
    req = request.Request(
        f'{connection_conf.base_url}{uri}',
        headers=connection_conf.general_header,
        data=json.dumps(data).encode("utf-8"),
        method='POST'
    )
    try:
        content = json.loads(
            request.urlopen(req).read().decode('utf-8')
        )[0]['payload']
    except Exception as e:
        global_var.LOGGER.error(
            f'publish message to {queue_name} failed with exception {e}.'
        )
        content = None
    return content


def consume_task():
    '''Retrieve tasks from rabbitmq and run test.
    '''
    while True:
        # declare queue.
        global_var.LOGGER.info(
            f'declaring queue {global_var.RUNNERCONF.runner_name}...'
        )
        if declare_queue(
            global_var.RUNNERCONF.runner_name,
            global_var.MQCONNCONF
        ) != 0: return

        # get length of queue.
        global_var.LOGGER.info(
            f'get length of queue {global_var.RUNNERCONF.runner_name}...'
        )
        while True:
            queue_length = get_queue_length(
                global_var.RUNNERCONF.runner_name,
                global_var.MQCONNCONF
            )
            if queue_length > 0:   break
            if queue_length == 0:  time.sleep(10)
            if queue_length < 0:   return
        
        # get a message from queue.
        global_var.LOGGER.info(
            f'getting message from {global_var.RUNNERCONF.runner_name}...'
        )
        message = get_message(
            global_var.RUNNERCONF.runner_name,
            global_var.MQCONNCONF,
            True
        )
        if message is None: return

        test_config = json.loads(message)
        test_config['Test']['TestBed'] = os.path.join(
            global_var.RUNNERCONF.output_dir,
            '_'.join(
                [
                    test_config['OS'],
                    test_config['SDK'],
                    test_config['Tool_Info']['version'],
                    datetime.now().strftime('%Y%m%d%H%M%S')
                ]
            )  
        )
        test_bed = test_config['Test']['TestBed']
        global_var.LOGGER.info(f'run diagnostics test in {test_bed}.')
        AutomationScripts.config.configuration = \
            AutomationScripts.config.GlobalConfig(test_config)
        AutomationScripts.run_test.run_test()

        global_var.LOGGER.info(
            f'remove message from {global_var.RUNNERCONF.runner_name}.'
        )
        if get_message(
            global_var.RUNNERCONF.runner_name,
            global_var.MQCONNCONF,
            False
        ) is None: return
        global_var.LOGGER.info(f'task run in {test_bed} is completed.')
        
        if queue_length - 1 > 0:
            continue
        else:
            time.sleep(60)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--output',
                        required=True,
                        help='the directory to store output.')
    args = parser.parse_args()

    output_dir = args.output

    time_stamp = datetime.now().strftime('%Y%m%d%H%M%S')
    global_var.LOGGER = Logger(
        'diagnostics runner',
        os.path.join(output_dir, f'{time_stamp}.log')
    )
    global_var.MQCONNCONF = MQConnectionConf(
        os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            'rabbitmq.ini'
        )
    )
    global_var.RUNNERCONF = RunnerConf(
        os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            'runner.ini'
        )
    )
    global_var.RUNNERCONF.output_dir = output_dir
    global_var.RUNNERCONF.init()

    consume_task()
