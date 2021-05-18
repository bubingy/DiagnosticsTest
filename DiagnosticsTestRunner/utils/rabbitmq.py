# coding=utf-8

import json
from urllib import request

import global_var
from utils.conf import MQConnectionConf


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
