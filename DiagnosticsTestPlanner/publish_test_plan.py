# coding=utf-8

import os
import json
import argparse

from WeeklyTestPlanner import weekly_test_planner
from ReleaseTestPlanner import release_test_planner
from utils.rabbitmq import declare_queue, publish_message
from utils.conf import MQConnectionConf, TestConf


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--type', choices=['weekly', 'release'])
    args = parser.parse_args()
    test_type = args.type

    connection_conf = MQConnectionConf(
        os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            'conf',
            'rabbitmq.ini'
        )
    )

    if test_type == 'release':
        test_conf = TestConf(
            os.path.join(
                os.path.dirname(os.path.abspath(__file__)),
                'conf',
                'release_test.ini'
            )
        )
        plans = release_test_planner.get_plans(test_conf)
    else:
        plans = weekly_test_planner.get_plans()
  
    for plan in plans:
        try:
            declare_queue(plan['OS'], connection_conf)
            publish_message(json.dumps(plan), plan['OS'], connection_conf)
        except Exception as e:
            os_name = plan['OS']
            print(f'exception when publishing {os_name}: {e}')
