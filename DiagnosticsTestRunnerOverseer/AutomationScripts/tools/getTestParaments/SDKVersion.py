# coding=utf-8

from urllib import request

from configuration import BRANCHES, RID

def get_sdk_version():
    '''Print out latest `release` version of .net core 3, .net 5 and .net 6.

    '''
    sdk_version = dict()
    for key in BRANCHES.keys():
        branch = BRANCHES[key]
        if branch[0] == '3':
            url = ('https://dotnetcli.blob.core.windows.net/'
                    f'dotnet/Sdk/release/{branch}/latest.version')
        else:
            url = f'https://aka.ms/dotnet/{branch}/daily/productCommit-{RID}.txt'
        
        response = request.urlopen(url)
        version = response.readlines()[-1].decode().strip('\r\n\t')
        sdk_version[key] = version
    return sdk_version
