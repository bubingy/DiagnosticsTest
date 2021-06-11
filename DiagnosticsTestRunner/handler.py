import os
import json
import pickle
import asyncio
import datetime

from utils.log import Logger
from utils.conf import RunnerConf
from SimpleRPC import BaseClientStreamHandler
from AutomationScripts import config


class ClientStreamHandler(BaseClientStreamHandler):
    def __init__(self,
                 runner_conf: RunnerConf,
                 logger: Logger) -> None:
        super().__init__()
        self.runner_conf = runner_conf
        self.logger = logger

    async def connect_to_server(self, host: str, port: int) -> None:
        self.logger.info('connecting to task proxy server...')
        self.reader, self.writer = await asyncio.open_connection(host, port)
        self.logger.info('connected to task proxy server...')
        # TODO: uncomment the following code after the bug is fixed.
        # client_info = {
        #     'runner_name': self.runner_conf.runner_name,
        #     'host_name': self.runner_conf.host_name,
        # }
        # message = {
        #     'function_name': 'refresh_status',
        #     'function_args': (client_info,),
        #     'function_kwargs': dict()
        # }
        # self.logger.info('sending heart beaten to task proxy server...')
        # while True:
        #     self.send(self.writer, message)
        #     await asyncio.sleep(5)

    async def communicate_with_server(self) -> None:
        client_info = {
            'runner_name': self.runner_conf.runner_name,
            'host_name': self.runner_conf.host_name,
        }
        retrieve_task = {
            'function_name': 'retrieve_task',
            'function_args': (client_info,),
            'function_kwargs': dict()
        }
        update_status = {
            'function_name': 'update_status',
            'function_args': (client_info, 'idling'),
            'function_kwargs': dict()
        }
        while True:
            self.logger.info('retrieving task...')
            self.send(self.writer, retrieve_task)
            plan = json.loads(pickle.loads(await self.receive(self.reader)))
            self.logger.info('get a task, start running...')
            self.call('run_task', (plan, self.runner_conf))

            self.send(self.writer, update_status)
            await asyncio.sleep(10)



def run_task(test_config, runner_conf: RunnerConf) -> None:
    '''Retrieve tasks from rabbitmq and run test.
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