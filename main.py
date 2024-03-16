import os

import app
from app import AppLogger
from tools import dotnet


testbed = 'D:\\Workspace\\testbed'
logger_path = os.path.join(testbed, 'test.log')
app.logger = AppLogger('test', logger_path)

rid = 'win-x64'
script_path = os.path.join(testbed, 'dotnet-install.ps1')
script_path = dotnet.donwload_install_script(rid, script_path)
script_path = dotnet.enable_runnable(rid, script_path)

sdk_version = '6.0.420'
dotnet_root = os.path.join(testbed, '.dotnet-test')
dotnet_root = dotnet.install_sdk_from_script(rid, script_path, sdk_version, dotnet_root)
print(script_path)