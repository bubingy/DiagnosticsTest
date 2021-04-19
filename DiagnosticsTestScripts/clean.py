# coding=utf-8

import os
import shutil

from config import configuration


if __name__ == '__main__':
    if 'win' in configuration.rid: home_path = os.environ['USERPROFILE']
    else: home_path = os.environ['HOME']

    to_be_removed = [
        os.path.join(home_path, '.aspnet'),
        os.path.join(home_path, '.dotnet'),
        os.path.join(home_path, '.nuget'),
        os.path.join(home_path, '.templateengine'),
        os.path.join(home_path, '.lldb'),
        os.path.join(home_path, '.lldbinit'),
        configuration.test_bed
    ]

    print('Following files or dirs would be removed:')
    for f in to_be_removed: print(f'    {f}')
    key = input('input `y` to continue, other input will be take as a no:')
    if key != 'y': exit(0)

    for f in to_be_removed:
        if not os.path.exists(f): continue
        if os.path.isdir(f): shutil.rmtree(f)
        else: os.remove(f)