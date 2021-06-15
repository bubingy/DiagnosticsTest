import os
import time
import json
import pickle
import socket
from datetime import datetime
from threading import Thread, Lock
from typing import Any

from utils.log import Logger
from utils.conf import RunnerConf, ProxyServerConf
from AutomationScripts import config


class ClientHandler:
    def __init__(self,
                 proxy_server_conf: ProxyServerConf,
                 runner_conf: RunnerConf,
                 logger: Logger) -> None:
        self.runner_conf = runner_conf
        self.logger = logger
        self.lock = Lock()

        self.host, self.port = proxy_server_conf.host, proxy_server_conf.port
        self.logger.info('connecting to task proxy server...')
        self.conn = socket.socket()
        self.conn.connect((self.host, self.port))
        self.logger.info('connected to task proxy server...')

    def receive(self) -> bytes:
        data = b''
        try:
            body_size = int.from_bytes(self.conn.recv(8), 'big')
        except Exception as e:
            print(e)
            return None
        while body_size > 0:
            buffer_size = min(4096, body_size)
            buffer = self.conn.recv(buffer_size)
            data += buffer
            body_size -= buffer_size
        return data

    def send(self, data: Any) -> None:
        message = b''
        try:
            body = pickle.dumps(data)
        except Exception as e:
            print(f'fail to dump message: {e}')
            return
        body_size = len(body)
        message += body_size.to_bytes(8, 'big')
        message += body
        self.conn.send(message)

    def send_heart_beaten(self):
        client_info = {
            'runner_name': self.runner_conf.runner_name,
            'host_name': self.runner_conf.host_name,
        }
        message = {
            'function_name': 'refresh_status',
            'function_args': (client_info,),
            'function_kwargs': dict()
        }
        self.logger.info('sending heart beaten to task proxy server...')
        while True:
            self.lock.acquire()
            self.send(message)
            self.lock.release()
            time.sleep(5)

    def retrieve_task(self) -> None:
        client_info = {
            'runner_name': self.runner_conf.runner_name,
            'host_name': self.runner_conf.host_name,
        }
        retrieve_task_call_request = {
            'function_name': 'retrieve_task',
            'function_args': (client_info,),
            'function_kwargs': dict()
        }

        while True:
            self.logger.info('retrieving task...')
            self.send(retrieve_task_call_request)
            result = self.receive()
            plan = json.loads(pickle.loads(result))
            self.logger.info('get a task, start running...')
            self.send(
                {
                    'function_name': 'update_status',
                    'function_args': (client_info, 'running'),
                    'function_kwargs': dict()
                }
            )
            run_task(plan, self.runner_conf)
            self.send(
                {
                    'function_name': 'update_status',
                    'function_args': (client_info, 'idling'),
                    'function_kwargs': dict()
                }
            )
            time.sleep(10)


class RunnerClient:
    def __init__(self, handler: ClientHandler) -> None:
        self.handler = handler

    def start_communicate(self):
        t1 = Thread(target=self.handler.send_heart_beaten)
        t2 = Thread(target=self.handler.retrieve_task)
        t1.start()
        t2.start()
        t1.join()
        t2.join()


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