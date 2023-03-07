# DotNet SDK
sdk_version_list: list = None
sdk_buildid_list: list = None

# Diagnostic Tools
tool_version: str = None
tool_feed: str = None

# Test
test_name: str = None
rid: str = None

# Analyze config
analyze_testbed_root: str = None
analyze_testbed: str = None

# Validate config
validate_testbed: str = None

# Container
docker_base_url: str = None
dockerfile_url: str = None
full_tag: str = None
# MountDir is a directory on the host which will be mounted to TestBed
mount_dir: list = None
security_opt: list = None
cap_add: list = None
privileged: bool = None

# environment variables
env: dict = None