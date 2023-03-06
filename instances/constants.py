import os
import sys

script_root = os.path.dirname(
    os.path.abspath(sys.argv[0])
)

assets_root = os.path.join(script_root, 'assets')
configuration_root = os.path.join(script_root, 'configuration')

linux_list = [
    'alpine3.15', 'centos8', 'debian10', 'debian11', 'fedora30', 'fedora31',
    'opensuse15.1', 'opensuse15.2', 'ubuntu16.04', 'ubuntu18.04', 'ubuntu20.04'
]
