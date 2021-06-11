import os
from datetime import datetime

from utils.log import Logger
from utils.conf import RunnerConf, ProxyServerConf
from SimpleRPC import *
from handler import ClientStreamHandler, run_task

if __name__ == "__main__":
    conf_dir = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        'conf'
    )
    proxy_server_conf = ProxyServerConf(os.path.join(conf_dir, 'proxyserver.ini'))
    runner_conf = RunnerConf(os.path.join(conf_dir, 'runner.ini'))

    output_dir = runner_conf.output_folder
    time_stamp = datetime.now().strftime('%Y%m%d%H%M%S')
    logger = Logger(
        'diagnostics runner',
        os.path.join(output_dir, f'{time_stamp}.log')
    )

    client_handler = ClientStreamHandler(runner_conf, logger)
    client_handler.register_function(run_task)

    client = RPCClient(client_handler)
    client.start_communicate(proxy_server_conf.host, proxy_server_conf.port)
