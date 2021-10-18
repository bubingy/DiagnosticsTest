'''Run LTTng test.'''

# coding=utf-8

import os

import init
from Projects import project
from config import GlobalConfig


if __name__ == "__main__":
    if os.geteuid() != 0:
        print('You need root permissions.')
        exit()
    global_conf = GlobalConfig()
    for idx, _ in enumerate(global_conf.sdk_version_list):
        conf = global_conf.get(idx)
        init.prepare_test_bed(conf)
        init.install_sdk(conf)
        init.download_perfcollect(conf)
        project.create_publish_project(conf, 'gcperfsim')
        proc = project.run_project(conf, 'gcperfsim')

        trace_path = os.path.join(
            conf.trace_directory,
            f'trace_net{conf.sdk_version}_{conf.rid}'
        )
        project.collect_trace(conf)
        proc.terminate()
