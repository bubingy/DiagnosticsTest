import glob
import time

from instances.config import DiagnosticToolsTest as diag_tools_test_conf
from instances.logger import ScriptLogger
from instances.project import webapp as webapp_config
from services.terminal import run_command_sync, PIPE
from services.project import webapp as webapp_service


def test_dotnet_stack(logger: ScriptLogger):
    '''Run sample apps and perform tests.

    '''
    tool_name = 'dotnet-stack'
    tool_path_pattern = (
        f'{diag_tools_test_conf.tool_root}/.store/{tool_name}'
        f'/{diag_tools_test_conf.tool_version}/{tool_name}'
        f'/{diag_tools_test_conf.tool_version}/tools/*/any/{tool_name}.dll'
    )
    tool_path = glob.glob(tool_path_pattern)[0]
    tool_bin = f'{diag_tools_test_conf.dotnet_bin_path} {tool_path}'
    
    logger.info(f'test {tool_name}')
    if webapp_config.runnable is False:
        logger.info(f'can\'t run webapp for {tool_name}.')
        logger.info(f'test {tool_name} finished')
        return
    
    proc = webapp_service.run_webapp(diag_tools_test_conf.env, diag_tools_test_conf.testbed)
    
    sync_commands_list = [
        f'{tool_bin} --help',
        f'{tool_bin} ps',
        f'{tool_bin} report -p {proc.pid}'
    ]
    for command in sync_commands_list:
        outs, errs = run_command_sync(
            command,
            cwd=diag_tools_test_conf.test_result_root,
            env=diag_tools_test_conf.env,
            stdout=PIPE,
            stderr=PIPE
        )
        logger.info(f'run command:\n{command}\n{outs}')
        if errs != '': logger.error(errs)

    proc.terminate()
    while proc.poll() is None:
        time.sleep(1)

    logger.info(f'test {tool_name} finished')
