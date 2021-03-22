# Tool Set
## getTestParaments
In order to get test paraments quickly, we develop `getTestParaments` in `tools` directory.  
Run following command on windows:
```
cd tools/getTestParaments
python get_test_paraments.py
```
The tool will print out sdk version, tool version and PR info.  

Retrieving version of diagnostics tool requires authority. Once you can't get tool version any more, try following steps:
1. open https://dev.azure.com/dnceng/internal/_build?definitionId=528&_a=summary in web browser in debug mode;
2. select `network` tab;
3. choose `_build?definitionId=528&_a=summary`;
4. Copy value of `cookie` in `Request Headers`;
5. Replace value of `cookie` in `tools/getTestParaments/configuration.py` with what you copied in step 4;
6. Re-run the tool.

## OSRotationGenerator
Not sure what OSes we will test against this week? Have no idea which sdk version we should choose for specific OS? That is why we develop this tool.
Run following command on windows:
```
cd tools/OSRotationGenerator
python get_os_rotation.py
```