# coding=utf-8

import copy
import datetime

from WeeklyTestPlanner.OSRotation.get_os_rotation import get_os_rotation
from WeeklyTestPlanner.TestParaments.SDKVersion import get_sdk_version
from WeeklyTestPlanner.TestParaments.ToolInfo import get_tool_info


def get_plans() -> list:
    plans = list()

    os_rotation = get_os_rotation(
        datetime.datetime.today().strftime('%Y-%m-%d')
    )
    tool_version, pr_info, tool_feed = get_tool_info()

    sdk_version, source_feed_version = get_sdk_version()
    for key in os_rotation['requiredOS']:
        plan = dict()
        plan['OS'] = key
        plan['SDK'] = sdk_version[os_rotation['requiredOS'][key]]
        plan['Source_Feed'] = source_feed_version[os_rotation['requiredOS'][key]]
        plan['Tool_Info'] = dict()
        plan['Tool_Info']['version'] = tool_version
        plan['Tool_Info']['commit'] = pr_info['commit']
        plan['Tool_Info']['feed'] = tool_feed
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
        plan['Source_Feed'] = source_feed_version[key]
        plan['Tool_Info'] = dict()
        plan['Tool_Info']['version'] = tool_version
        plan['Tool_Info']['commit'] = pr_info['commit']
        plan['Tool_Info']['feed'] = tool_feed
        plan['Test'] = dict()
        plan['Test']['RunBenchmarks'] = plan['SDK'][0] == '3'
        plans.append(plan)

        # this is temp plan
        if plan['SDK'][0] == '6':
            ext_plan = copy.deepcopy(plan)
            ext_plan['OS'] = plan['OS'] + 'EXT'
            plans.append(ext_plan)

    return plans
