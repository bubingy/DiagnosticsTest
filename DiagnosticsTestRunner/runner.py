# coding=utf-8

import os
import time
import json
import argparse
from datetime import datetime

import pika

import global_var
from utils import RunnerConfig, Logger
from AutomationScripts import config


def retrieve_task():
    '''Retrieve tasks from rabbitmq.
    '''
    # establish connection to rabbitmq
    while True:
        global_var.LOGGER.info('establish connection to rabbitmq.')
        try:
            connection = pika.BlockingConnection(
                pika.URLParameters(
                    global_var.RUNNERCONF.rabbitmq_url
                )
            )
            channel = connection.channel()
            res = channel.queue_declare(queue=global_var.RUNNERCONF.runnername)
            if res.method.message_count == 0:
                connection.close()
                break
            
            
            global_var.LOGGER.info(f'retrieving message from {global_var.RUNNERCONF.runnername}...')
            _, _, body = channel.basic_get(
                global_var.RUNNERCONF.runnername,
                True # turn to True before deploying.
            )
            connection.close()
        except Exception as e:
            global_var.LOGGER.error(f'fail to retrieve tasks, Exception info: {e}')
            connection.close()
            return

        test_config = json.loads(body.decode('utf-8'))
        test_config['Test']['TestBed'] = os.path.join(
            global_var.RUNNERCONF.output_dir,
            '_'.join(
                [
                    test_config['OS'],
                    test_config['SDK'],
                    test_config['Tool_Info']['version'],
                    datetime.now().strftime('%Y%m%d%H%M%S')
                ]
            )  
        )
        test_bed = test_config['Test']['TestBed']
        global_var.LOGGER.info(f'run diagnostics test in {test_bed}.')
        config.configuration = config.GlobalConfig(test_config)
        from AutomationScripts import run_test
        run_test.run_test()
        global_var.LOGGER.info(f'task run in {test_bed} is completed.')
    return


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--output',
                        required=True,
                        help='the directory to store output.')
    default_conf_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        'conf.ini'
    )
    parser.add_argument('--ini',
                        default=default_conf_path,
                        help='path of configuration file.')
    args = parser.parse_args()

    output_dir = args.output
    conf_file_path = args.ini

    time_stamp = datetime.now().strftime('%Y%m%d%H%M%S')
    global_var.LOGGER = Logger(
        'diagnostics runner',
        os.path.join(output_dir, f'{time_stamp}.log')
    )
    global_var.RUNNERCONF = RunnerConfig(conf_file_path)
    global_var.RUNNERCONF.__setattr__('output_dir', output_dir)

    while True:
        time.sleep(30)
        retrieve_task()
