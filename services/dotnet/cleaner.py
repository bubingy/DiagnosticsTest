import os
import shutil

from instances.logger import ScriptLogger


def remove_test_temp_directory(rid: str, logger: ScriptLogger=None):
    if 'win' in rid: home_path = os.environ['USERPROFILE']
    else: home_path = os.environ['HOME']

    to_be_removed = [
        os.path.join(home_path, '.aspnet'),
        os.path.join(home_path, '.debug'),
        os.path.join(home_path, '.dotnet'),
        os.path.join(home_path, '.nuget'),
        os.path.join(home_path, '.templateengine'),
        os.path.join(home_path, '.lldb'),
        os.path.join(home_path, '.lldbinit'),
        os.path.join(home_path, 'lttng-traces'),
        os.path.join(home_path, '.local')
    ]

    for f in to_be_removed:
        if not os.path.exists(f): continue
        try:
            if os.path.isdir(f): shutil.rmtree(f)
            else: os.remove(f)
        except Exception as e:
            if logger is not None:
                logger.error(f'fail to remove {f}: {e}')