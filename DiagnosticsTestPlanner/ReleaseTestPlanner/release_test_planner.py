# coding=utf-8

from utils.conf import ReleaseTestConf


def get_plans(test_conf: ReleaseTestConf) -> list:
    plans = list()
    for source_feed, sdk in zip(test_conf.source_feed_list, test_conf.sdk_list):
        for os_name in test_conf.os_list:
            plan = dict()
            plan['OS'] = os_name
            plan['SDK'] = sdk
            plan['Source_Feed'] = source_feed
            plan['Tool_Info'] = dict()
            plan['Tool_Info']['version'] =  test_conf.tool_version
            plan['Tool_Info']['commit'] = None
            plan['Tool_Info']['feed'] = test_conf.tool_feed
            plan['Test'] = dict()
            plan['Test']['RunBenchmarks'] = False
            plans.append(plan)
    return plans
