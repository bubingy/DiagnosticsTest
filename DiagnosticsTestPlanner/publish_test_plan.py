# coding=utf-8

import os
import json
import argparse

from WeeklyTestPlanner import weekly_test_planner
from ReleaseTestPlanner import release_test_planner
from utils.conf import ReleaseTestConf, RedisConnection


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--type', choices=['weekly', 'release'])
    args = parser.parse_args()
    test_type = args.type

    redis_conn = RedisConnection(
        os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            'conf',
            'redis.ini'
        )
    )

    if test_type == 'release':
        test_conf = ReleaseTestConf(
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
        os_name = plan['OS']
        try:
            redis_conn.diagnostics_task_table_conn.rpush(os_name, json.dumps(plan))
        except Exception as e:
            print(f'exception when publishing {os_name}: {e}')
