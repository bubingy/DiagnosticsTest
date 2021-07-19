import os
from datetime import datetime
from threading import Thread, Lock

from handler import RunnerHandler
from utils.log import Logger
from utils.conf import RunnerConf, RedisClient


if __name__ == "__main__":
    conf_dir = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        'conf'
    )
    runner_conf = RunnerConf(os.path.join(conf_dir, 'runner.ini'))

    output_dir = runner_conf.output_folder
    time_stamp = datetime.now().strftime('%Y%m%d%H%M%S')
    logger = Logger(
        'diagnostics runner',
        os.path.join(output_dir, f'{time_stamp}.log')
    )

    redis_client = RedisClient(os.path.join(conf_dir, 'redis.ini'))
    
    runner_handler = RunnerHandler(runner_conf, redis_client, logger)
    runner_handler.retrieve_task()
