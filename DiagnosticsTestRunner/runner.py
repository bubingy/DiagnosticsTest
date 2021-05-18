# coding=utf-8

import os
import time
import json
import argparse
from datetime import datetime

import global_var
from AutomationScripts import config
from utils.rabbitmq import get_message, get_queue_length, declare_queue
from utils.log import Logger
from utils.conf import MQConnectionConf, RunnerConf


def consume_task():
    '''Retrieve tasks from rabbitmq and run test.
    '''
    while True:
        # declare queue.
        global_var.LOGGER.info(
            f'declaring queue {global_var.RUNNERCONF.runner_name}...'
        )
        if declare_queue(
            global_var.RUNNERCONF.runner_name,
            global_var.MQCONNCONF
        ) != 0: return

        # get length of queue.
        while True:
            queue_length = get_queue_length(
                global_var.RUNNERCONF.runner_name,
                global_var.MQCONNCONF
            )
            if queue_length > 0:   break
            if queue_length == 0:  time.sleep(10)
            if queue_length < 0:   return
        
        # get a message from queue.
        global_var.LOGGER.info(
            f'getting message from {global_var.RUNNERCONF.runner_name}...'
        )
        message = get_message(
            global_var.RUNNERCONF.runner_name,
            global_var.MQCONNCONF,
            False
        )
        if message is None: continue

        test_config = json.loads(message)
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
        from AutomationScripts import main
        main.run_test()

        global_var.LOGGER.info(f'task run in {test_bed} is completed.')
        
        if queue_length - 1 > 0:
            continue
        else:
            time.sleep(60)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--output',
                        required=True,
                        help='the directory to store output.')
    args = parser.parse_args()

    output_dir = args.output

    time_stamp = datetime.now().strftime('%Y%m%d%H%M%S')
    global_var.LOGGER = Logger(
        'diagnostics runner',
        os.path.join(output_dir, f'{time_stamp}.log')
    )
    global_var.MQCONNCONF = MQConnectionConf(
        os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            'conf',
            'rabbitmq.ini'
        )
    )
    global_var.RUNNERCONF = RunnerConf(
        os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            'conf',
            'runner.ini'
        )
    )
    global_var.RUNNERCONF.output_dir = output_dir
    global_var.RUNNERCONF.init()

    consume_task()
