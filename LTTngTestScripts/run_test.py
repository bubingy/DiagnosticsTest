'''Run LTTng test.'''

# coding=utf-8

import os

import init
from Projects import project
from config import GlobalConfig
from clean import get_remove_candidate, do_clean

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
        project.collect_trace(conf)
        proc.terminate()

        to_be_removed = get_remove_candidate(global_conf)
        do_clean(to_be_removed)