BRANCHES = {
    '.net core 3.1':'3.1.4xx',
    '.net 5.0': '5.0.3XX',
    '.net 6.0': '6.0.1XX-preview2'
}

RID = 'win-x64'

RESULTS = [
    'succeeded',
    'partiallySucceeded'
]

# VERY IMPORTANT:
# IF THE FOLLOWING HEADER DOSE NOT WORK ANY MORE, 
# OPEN FOLLOWING LINK WITH WEB BROWSER(DEBUG MOD REQUIRED),
# REPLACE VALUE OF `cookie` WITH which IN `Request Header` FIELD.
#   https://dev.azure.com/dnceng/internal/_build?definitionId=528&_a=summary
HEADERS = {
    'cookie': (
        'VstsSession=%7B%22PersistentSessionId%22%3A%22ff6c5164'
        '-c640-4b9f-ab08-9233b5e38cac%22%2C%22'
        'PendingAuthenticationSessionId%22%3A%2200000000'
        '-0000-0000-0000-000000000000%22%2C%22'
        'CurrentAuthenticationSessionId%22%3A%22f88875ba'
        '-3633-4049-b288-4121b8160f24%22%2C%22'
        'SignInState%22%3A%7B%7D%7D; '
        'UserAuthentication=eyJ0eXAiOiJKV1QiLCJhbGciOiJSUz'
        'I1NiIsIng1dCI6IjRkZWF3MFZZVnlPd05BSFh0YjZWZ3hrYzQ'
        '2TSJ9.eyJmYW1pbHlfbmFtZSI6IkJ1IiwiZ2l2ZW5fbmFtZSI6Il'
        'ZpbmNlbnQiLCJvaWQiOiI0MzYwODNkMC03YmIzLTRmN2ItYTI5OC1'
        'mZTE3M2JhMTU3MjYiLCJ0aWQiOiI3MmY5ODhiZi04NmYxLTQxYWYtOT'
        'FhYi0yZDdjZDAxMWRiNDciLCJzdWIiOiI3MmY5ODhiZi04NmYxLTQx'
        'YWYtOTFhYi0yZDdjZDAxMWRiNDdcXHYtYmlidUBtaWNyb3NvZnQuY29'
        'tIiwidW5pcXVlX25hbWUiOiJ2LWJpYnVAbWljcm9zb2Z0LmNvbSIsImV'
        'tYWlsIjoidi1iaWJ1QG1pY3Jvc29mdC5jb20iLCJwdWlkIjoiYWFkOjEw'
        'MDM3RkZFQUMzREQxRTUiLCJ2ZXIiOiIxLjAiLCJqdGkiOiI5YzUwODI'
        '0My1iMTBiLTQ5OGQtODYzNS0zZjk0MWZlZGE3Y2YiLCJpc3MiOiJhcHA'
        'udnN0b2tlbi52aXN1YWxzdHVkaW8uY29tIiwiYXVkIjoiZTVjODY2NzYt'
        'ZDA2My00ZGEzLWJiOTYtYzhlMDUwNGJkYmE1IiwibmJmIjoxNjE1ODgwNj'
        'I0LCJleHAiOjE2MTY0ODU0MjR9.V-7IuqKJjMRx8AAQHj4ogMHmPsr2YOni'
        '5AyJgIqgzIlOe2ubzr9erkvKY_qqtEIqRvnMtlyjnO4zS48TjWn-iJEQzD_X'
        'Tds-C_nMcWZcrIP1MX8KhL5fLlpuYYR-6xQT2fWWARM_R40_GMIxy6B-8NPV'
        'hLrF7DhQ5B3vyb3WweOaGZysyGghtiLWTBx7eYqscvX9GTz1x0g5G5tNU9'
        'cK6ZoqGJznqSla_MWmDyQ8qGeF9jS0OR0kzeTcO_KQny1nQqPvG65pm0Uw'
        'sslpUO1OwXbhcn-VnXcVENQcclc-v7DydHHLduF-2wJDjBNqSB0bUKk0O2V'
        'OHkrmqPnuCGTeFg; X-VSS-UseRequestRouting=True; __RequestVe'
        'rificationToken=ZW5GTJ_0AdoJ7QYjf8bfD4aaiuOg2IYZ0Wt0hw42oUt'
        'pydeqX3zGNWkT8UXp53Y8c0KaMFGwhCyZPK8MF8rX3SKtTa01; __Reques'
        'tVerificationToken2e8a20ef0-4cf2-488e-a553-e540d65db1ea=ZW5G'
        'TJ_0AdoJ7QYjf8bfD4aaiuOg2IYZ0Wt0hw42oUtpydeqX3zGNWkT8UXp53Y'
        '8c0KaMFGwhCyZPK8MF8rX3SKtTa01'
    )
}