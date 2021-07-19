import os
import time
import json
import pickle
from datetime import datetime
from threading import Lock

from utils.conf import RunnerConf, RedisClient
from utils.log import Logger
from AutomationScripts import config


class RunnerHandler:
    def __init__(self,
                 runner_conf: RunnerConf,
                 redis_client: RedisClient,
                 logger: Logger) -> None:
        self.runner_conf = runner_conf
        self.redis_client = redis_client
        self.logger = logger
        self.mutex = Lock()

    def update_status(self) -> None:
        key_name = f'{self.runner_conf.runner_name}@{self.runner_conf.host_name}'

        self.redis_client.run_command('SELECT 0')
        
        status = self.redis_client.run_command(f'GET {key_name}')
        if status is None:
            self.redis_client.run_command(f'SET {key_name} idling EX 10')
        else:
            self.redis_client.run_command(f'SET {key_name} {status} EX 10')

    def retrieve_task(self) -> None:
        while True:
            key_name = f'{self.runner_conf.runner_name}@{self.runner_conf.host_name}'
            self.redis_client.run_command('SELECT 0')
            status = self.redis_client.run_command(f'GET {key_name}')
            if status is 'running':
                time.sleep(60)
                continue

            self.redis_client.run_command('SELECT 1')
            tasks_list_size = self.redis_client.run_command(
                f'LLEN {self.runner_conf.runner_name}'
            )
            if tasks_list_size <= 0:
                time.sleep(60)
                continue

            self.redis_client.run_command('SELECT 1')
            result = self.redis_client.run_command(
                f'RPOP {self.runner_conf.runner_name}'
            )
            plan = json.loads(pickle.loads(result))
            self.logger.info('get a task, start running...')
            
            self.update_status('running', self.runner_conf, self.redis_client)
            self.run_task(plan, self.runner_conf)
            self.update_status('idling', self.runner_conf, self.redis_client)

            time.sleep(10)

    def run_task(self, test_config: json, runner_conf: RunnerConf) -> None:
        '''Retrieve tasks from redis and run test.

        '''
        test_config['Test']['TestBed'] = os.path.join(
            runner_conf.output_folder,
            '_'.join(
                [
                    test_config['OS'],
                    test_config['SDK'],
                    test_config['Tool_Info']['version'],
                    datetime.now().strftime('%Y%m%d%H%M%S')
                ]
            )
        )
        config.configuration = config.GlobalConfig(test_config)
        from AutomationScripts import main
        main.run_test()