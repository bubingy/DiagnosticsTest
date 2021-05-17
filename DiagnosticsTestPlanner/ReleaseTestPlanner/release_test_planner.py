# coding=utf-8

import os
import json

from utils import TestConf, MQConnectionConf, declare_queue, publish_message


def get_plans() -> list:
    plans = list()
    test_conf = TestConf(
        os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            'release_test.ini'
        )
    )
    for sdk in test_conf.sdk_list:
        for os in test_conf.os_list:
            plan = dict()
            plan['OS'] = os
            plan['SDK'] = sdk
            plan['Tool_Info'] = dict()
            plan['Tool_Info']['version'] =  test_conf.tool_version
            plan['Tool_Info']['commit'] = None
            plan['Tool_Info']['feed'] = test_conf.tool_feed
            plan['Test'] = dict()
            plan['Test']['RunBenchmarks'] = False
            plans.append(plan)
    return plans


def publish_plan():
    connection_conf = MQConnectionConf(
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
    publish_plan()
