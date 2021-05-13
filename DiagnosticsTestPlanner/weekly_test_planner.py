# coding=utf-8

import os
import copy
import json
import datetime

from OSRotation.get_os_rotation import get_os_rotation
from TestParaments.SDKVersion import get_sdk_version
from TestParaments.ToolInfo import ToolInfo
from utils import AMQPConnectionConf, declare_queue, publish_message


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
        # TODO
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
    connection_conf = AMQPConnectionConf(
        os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            'rabbitmq.ini'
        )
    )
    plans = get_plans()
    
    for plan in plans:
        try:
            declare_queue(plan['OS'], connection_conf)
            publish_message(json.dumps(plan), plan['OS'], connection_conf)
        except Exception as e:
            os_name = plan['OS']
            print(f'exception when publishing {os_name}: {e}')


if __name__ == "__main__":
    # TODO: the test plan is still in change
    publish_plan()
    