# coding=utf-8

import os
import copy
import json
import datetime

import pika

from OSRotation.get_os_rotation import get_os_rotation
from TestParaments.SDKVersion import get_sdk_version
from TestParaments.ToolInfo import ToolInfo
from utils import load_json


def get_plans() -> list:
    plans = list()

    os_rotation = get_os_rotation(
        datetime.datetime.today().strftime('%Y-%m-%d')
    )
    tool_info = ToolInfo()

    sdk_version = get_sdk_version()
    for key in os_rotation['requiredOS']:
        plan = dict()
        plan['OS'] = key
        plan['SDK'] = sdk_version[os_rotation['requiredOS'][key]]
        plan['Tool_Info'] = dict()
        plan['Tool_Info']['version'] = tool_info.tool_version
        plan['Tool_Info']['commit'] = tool_info.pr_info['commit']
        plan['Tool_Info']['feed'] = tool_info.feed
        plan['Test'] = dict()
        plan['Test']['RunBenchmarks'] = plan['SDK'][0] == '3'
        plans.append(plan)

        # this is temp plan
        if plan['SDK'][0] == '6' and 'Alpine' in plan['OS']:
            ext_plan = copy.deepcopy(plan)
            ext_plan['OS'] = plan['OS'] + 'EXT'
            plans.append(ext_plan)

    for key in os_rotation['alternateOS']:
        plan = dict()
        plan['OS'] = os_rotation['alternateOS'][key]

        # we don't have arm32 device currently. 
        if 'LinuxCross' == plan['OS']: continue

        plan['SDK'] = sdk_version[key]
        plan['Tool_Info'] = dict()
        plan['Tool_Info']['version'] = tool_info.tool_version
        plan['Tool_Info']['commit'] = tool_info.pr_info['commit']
        plan['Tool_Info']['feed'] = tool_info.feed
        plan['Test'] = dict()
        plan['Test']['RunBenchmarks'] = plan['SDK'][0] == '3'
        plans.append(plan)

        # this is temp plan
        if plan['SDK'][0] == '6':
            ext_plan = copy.deepcopy(plan)
            ext_plan['OS'] = plan['OS'] + 'EXT'
            plans.append(ext_plan)

    return plans


def publish_plan():
    connection_info = load_json(
        os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            'conf',
            'connection.json'
        )
    )

    user = connection_info['user']
    password = connection_info['password']
    ip = connection_info['ip']
    port = connection_info['port']
    vhost = connection_info['vhost']

    connection = pika.BlockingConnection(
        pika.URLParameters(
            f'amqp://{user}:{password}@{ip}:{port}/{vhost}'
        )
    )
    channel = connection.channel()
    plans = get_plans()
    
    for plan in plans:
        try:
            channel.queue_declare(queue=plan['OS'])
            channel.basic_publish(
                exchange='',
                routing_key=plan['OS'],
                body=json.dumps(plan)
            )
        except Exception as e:
            os_name = plan['OS']
            print(f'exception when publishing {os_name}: {e}')
    connection.close()


if __name__ == "__main__":
    # TODO: the test plan is still in change
    publish_plan()
    