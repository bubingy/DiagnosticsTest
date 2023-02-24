import glob

from instances.config import DiagnosticToolsTest as diag_tools_test_conf
from instances.logger import ScriptLogger
from instances.project import webapp as webapp_config
from instances.project import consoleapp as consoleapp_config
from services.terminal import run_command_sync, PIPE
from services.project import webapp as webapp_service


def test_dotnet_trace(logger: ScriptLogger):
    '''Run sample apps and perform tests.

    '''
    tool_name = 'dotnet-trace'
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
    
    webapp_process = webapp_service.run_webapp(diag_tools_test_conf.env, diag_tools_test_conf.testbed)

    sync_commands_list = [
        f'{tool_bin} --help',
        f'{tool_bin} list-profiles',
        f'{tool_bin} ps',
        f'{tool_bin} collect -p {webapp_process.pid} -o webapp.nettrace --duration 00:00:10',
        f'{tool_bin} convert --format speedscope webapp.nettrace'
    ]
    for command in sync_commands_list:
        outs, errs = run_command_sync(
            command,
            env=diag_tools_test_conf.env,
            cwd=diag_tools_test_conf.test_result_root,
            stdout=PIPE,
            stderr=PIPE
        )
        logger.info(f'run command:\n{command}\n{outs}')
        if errs != '': logger.error(errs)

    webapp_process.terminate()
    webapp_process.communicate()

    if consoleapp_config.runnable is False:
        logger.info(f'can\'t run consoleapp for {tool_name}.')
        logger.info(f'test {tool_name} finished')
        return

    command = (
        f'{tool_bin} collect -o consoleapp.nettrace '
        '--providers Microsoft-Windows-DotNETRuntime '
        f'-- {consoleapp_config.project_bin_path}'
    )
    
    outs, errs = run_command_sync(
        command,
        env=diag_tools_test_conf.env,
        cwd=diag_tools_test_conf.test_result_root,
        stdout=PIPE,
        stderr=PIPE
    )
    logger.info(f'run command:\n{command}\n{outs}')
    if errs != '': logger.error(errs)

    logger.info(f'test {tool_name} finished')