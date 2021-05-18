# coding=utf-8

import json
from urllib import request

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
        print(f'fail to declare queue: {e}')
        return 1


def publish_message(message: str, queue_name: str, connection_conf: MQConnectionConf) -> int:
    '''Publish a message.

    :param message: message in string format.
    :param queue_name: name of queue.
    :param connection_conf: rabbitmq connection info.
    :return: 0 if successes, 1 if fails. 
    '''
    data = {
        'properties':{},
        'routing_key':queue_name,
        'payload':message,
        'payload_encoding':'string'
    }
    uri = f'/api/exchanges/{connection_conf.vhost}//publish'
    req = request.Request(
        f'{connection_conf.base_url}{uri}',
        headers=connection_conf.general_header,
        data=json.dumps(data).encode("utf-8"),
        method='POST'
    )
    try:
        request.urlopen(req).read().decode('utf-8')
        return 0
    except Exception as e:
        print(f'fail to publish message: {e}')
        return 1
