# DotNet SDK
sdk_version: str = None
sdk_buildid: str = None
sdk_root: str = None
dotnet_bin_path: str = None

# Diagnostic Tools
tool_version: str = None
tool_feed: str = None
tool_root: str = None

# Test
# absolute path or alias of lldb(linux/OSX) or cdb(Windows)
# if use alias, make sure the directory of debugger is in the PATH
debugger: str = None
test_name: str = None
rid: str = None

testbed: str = None
test_result_root: str = None

use_container: bool = None

# Container
docker_base_url: str = None
dockerfile_url: str = None
# MountDir is a directory on the host which will be mounted to TestBed
mount_dir: list = None
security_opt: list = None
cap_add: list = None
privileged: bool = None

logger = None

env: dict = None