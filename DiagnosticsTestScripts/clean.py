# coding=utf-8

import os

if __name__ == '__main__':
    files = [
        os.path.join(os.environ['HOME'], '.dotnet'),
        os.path.join(os.environ['HOME'], '.aspnet'),
        os.path.join(os.environ['HOME'], '.nuget'),
        os.path.join(os.environ['HOME'], '.templateengine'),
        os.path.join(os.environ['HOME'], '.lldb'),
        os.path.join(os.environ['HOME'], '.lldbinit'),
    ]
    for f in files:
        if not os.path.exists(f):
            continue

        if os.path.isdir(f): os.removedirs(f)
        else: os.remove(f)
