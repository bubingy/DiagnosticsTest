# DiagnosticsTest
This is automation script for diagnostic tool related tests.

## Diagnostics tools test
Before testing, modify `config.conf` in `DiagnosticsToolsTest`.  

To start diagnostics tool test, run
```
python test_diagnotics.py run
```
To clean all files and folders generated during the testing, run
```
python test_diagnotics.py clean
```

## CrossOSDAC test
Before testing, modify `config.conf` in `CrossOSDACTest`.  

First, generate dumps and analyze them on Linux by running:
```
python test_crossosdac.py analyze
```
Then, copy those dumps to Windows machine and analyze them with command:
```
python test_crossosdac.py validate
```

## LTTng test
Before testing, modify `config.conf` in `LTTngTest`.  

Run following command to start lttng test:
```
python test_lttng.py run
```