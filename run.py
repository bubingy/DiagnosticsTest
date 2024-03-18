import os

from DiagnosticTools import configuration


conf_file_path = 'E:\\Workspace\\DiagToolTask\\DiagnosticsTest\\TestConfiguration\\DiagToolsTest.conf'
conf = configuration.parse_conf_file(conf_file_path)
print(conf)