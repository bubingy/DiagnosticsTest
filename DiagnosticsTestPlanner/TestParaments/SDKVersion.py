# coding=utf-8

import os
import configparser
from urllib import request


def get_sdk_version():
    '''Print out latest `release` version of .net core 3, .net 5 and .net 6.

    '''
    configuration = configparser.ConfigParser()
    configuration.read(
        os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            'testargs.ini'
        )
    )

    branches = configuration['branches']

    sdk_version = dict()
    for key in branches.keys():
        branch = branches[key]
        if branch[0] == '3':
            url = ('https://dotnetcli.blob.core.windows.net/'
                    f'dotnet/Sdk/release/{branch}/latest.version')
        else:
            url = f'https://aka.ms/dotnet/{branch}/daily/productCommit-win-x64.txt'
        
        response = request.urlopen(url)
        version = response.readlines()[-1].decode().strip('\r\n\t')
        sdk_version[key] = version
    return sdk_version
