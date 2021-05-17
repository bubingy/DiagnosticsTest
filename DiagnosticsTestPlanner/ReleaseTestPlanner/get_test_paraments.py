# coding=utf-8

import argparse

from utils import os, TestConf, print_test_matrix


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--output')
    args = parser.parse_args()
    output_file = args.output

    test_conf = TestConf(
        os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            'release_test.ini'
        )
    )
    print_test_matrix(test_conf, output_file)