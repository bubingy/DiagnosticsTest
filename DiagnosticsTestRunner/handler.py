import json
import os
import pickle
import asyncio

from utils.log import Logger
from utils.conf import RunnerConf, ProxyServerConf
from SimpleRPC import BaseClientStreamHandler


class ClientStreamHandler(BaseClientStreamHandler):
    def __init__(self,
                 run_conf_file_path: os.PathLike,
                 proxyserver_conf_file_path: os.PathLike,
                 logger: Logger) -> None:
        super().__init__()
        self.runner_conf = RunnerConf(run_conf_file_path)
        self.proxyserver_conf = ProxyServerConf(proxyserver_conf_file_path)
        self.logger = logger

    async def connect_to_server(self, host: str, port: int) -> None:
        self.reader, self.writer = await asyncio.open_connection(host, port)
        client_info = {
            'runner_name': self.runner_conf.runner_name,
            'host_name': self.runner_conf.host_name,
        }
        message = {
            'function_name': 'refresh_status',
            'function_args': (client_info,),
            'function_kwargs': dict()
        }
        while True:
            self.send(self.writer, message)
            await asyncio.sleep(5)

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
            self.send(self.writer, retrieve_task)
            plan = json.loads(pickle.loads(await self.receive(self.reader)))
            self.call('', (plan,))  # TODO

            self.send(self.writer, update_status)
            await asyncio.sleep(10)