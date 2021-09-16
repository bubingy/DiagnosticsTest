# coding=utf-8

import os
import shutil

from config import GlobalConfig


def get_remove_candidate(global_conf: GlobalConfig) -> set:
    to_be_removed = set()
    for idx, _ in enumerate(global_conf.sdk_version_list):
        for arch in ['x86', 'x64']:
            conf = global_conf.get(idx, arch)
            if 'win' in conf.rid: home_path = os.environ['USERPROFILE']
            else: home_path = os.environ['HOME']
            to_be_removed = to_be_removed.union(
                {
                    os.path.join(home_path, '.aspnet'),
                    os.path.join(home_path, '.dotnet'),
                    os.path.join(home_path, '.nuget'),
                    os.path.join(home_path, '.templateengine'),
                    os.path.join(home_path, '.lldb'),
                    os.path.join(home_path, '.lldbinit'),
                    os.path.join(home_path, '.local'),
                    conf.dotnet_root,
                    conf.tool_root
                }
            )
            for f in os.listdir(conf.test_bed):
                if conf.dump_directory == os.path.join(conf.test_bed, f): continue
                if conf.analyze_output == os.path.join(conf.test_bed, f): continue

                to_be_removed.add(
                    os.path.join(conf.test_bed, f)
                )
    return to_be_removed


if __name__ == '__main__':
    global_conf = GlobalConfig()
    to_be_removed = get_remove_candidate(global_conf)
    print('Following files or dirs would be removed:')
    for f in to_be_removed: print(f'    {f}')
    key = input('input `y` to continue, other input will be take as a no:')
    if key != 'y': exit(0)

    for f in to_be_removed:
        if not os.path.exists(f): continue
        try:
            if os.path.isdir(f): shutil.rmtree(f)
            else: os.remove(f)
        except Exception as e:
            print(f'fail to remove {f}: {e}')

    