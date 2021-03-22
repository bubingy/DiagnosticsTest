# coding=utf-8

import datetime

import pika
import schedule

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
        
        plan['period'] = dict()
        plan['period']['monday'] = os_rotation['monday']
        plan['period']['friday'] = os_rotation['friday']

        plan['Tool_Info'] = dict()
        plan['Tool_Info']['version'] = tool_info.tool_version
        plan['Tool_Info']['commit'] = tool_info.pr_info['commit']
        plan['Tool_Info']['commit_html_url'] = tool_info.pr_info['commit_html_url']
        plan['Tool_Info']['pull'] = tool_info.pr_info['pull']
        plan['Tool_Info']['pull_html_url'] = tool_info.pr_info['pull_html_url']
        plans.append(plan)

    for key in os_rotation['alternateOS']:
        plan = dict()
        plan['OS'] = os_rotation['alternateOS'][key]
        plan['SDK'] = sdk_version[key]

        plan['period'] = dict()
        plan['period']['monday'] = os_rotation['monday']
        plan['period']['friday'] = os_rotation['friday']

        plan['Tool_Info'] = dict()
        plan['Tool_Info']['version'] = tool_info.tool_version
        plan['Tool_Info']['commit'] = tool_info.pr_info['commit']
        plan['Tool_Info']['commit_html_url'] = tool_info.pr_info['commit_html_url']
        plan['Tool_Info']['pull'] = tool_info.pr_info['pull']
        plan['Tool_Info']['pull_html_url'] = tool_info.pr_info['pull_html_url']
        plans.append(plan)

    return plans


def publish_plan():
    import os, json
    connection_info = load_json(
        os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
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

    rid_map_info = load_json(
        os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            'RIDMap.json'
        )
    )
    
    for plan in plans:
        try:
            channel.basic_publish(
                exchange='',
                routing_key=rid_map_info[plan['OS']],
                body=json.dumps(plan)
            )
        except Exception as e:
            os_name = plan['OS']
            print(f'exception when publishing {os_name}: {e}')


if __name__ == "__main__":
    schedule.every().wednesday.at("9:00").do(get_plans)