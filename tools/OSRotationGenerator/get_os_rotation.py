# coding=utf-8

import os
import json
import datetime
import argparse
from typing import Any


def load_json(file_path: os.PathLike) -> Any:
    import json
    content = None
    with open(file_path, 'r') as reader:
        content = reader.read()
    content = json.loads(content)
    return content


def calculate_week_increment(date_str: str) -> int:
    '''Calculate how much weeks between given day and week in `baseStatus.json`.

    Args:
        date_str - a string object in format `year-month-day`.
    Return: number of weeks between given day and week in `baseStatus.json`.
    '''
    base_status = load_json(
        os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            'baseStatus.json'
        )
    )
    year, month, day = date_str.split('-')
    date_obj = datetime.datetime(
        year=int(year),
        month=int(month),
        day=int(day)
    )
    base_year, base_month, base_day = base_status['monday'].split('-')
    base_date_obj = datetime.datetime(
        year=int(base_year),
        month=int(base_month),
        day=int(base_day)
    )
    day_increment = (date_obj - base_date_obj).days
    if day_increment < 0:
        if day_increment % 7 == 0:
            return - (abs(day_increment) // 7)
        else:
            return - (abs(day_increment) // 7) - 1
    else:
        return day_increment // 7


def get_required_os_status(date_str: str) -> dict:
    '''Get the sdk major versions for required OSes.

    Args:
        date_str - a string object in format `year-month-day`.
    Return: a dict object in format
        {
            `required_os1` = `sdk major version1`
            `required_os2` = `sdk major version2`
                            ...
        }
    '''
    base_status = load_json(
        os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            'baseStatus.json'
        )
    )

    required_oses = list(base_status['requiredOS'].keys())
    dotnet_major_versions = list()
    for required_os in required_oses:
        dotnet_major_versions.append(base_status['requiredOS'][required_os])
    
    week_increment = calculate_week_increment(date_str)
    if week_increment > 0:
        for _ in range(week_increment):
            poped_version = dotnet_major_versions.pop(0)
            dotnet_major_versions.append(poped_version)
    if week_increment < 0:
        for _ in range(week_increment, 0):
            poped_version = dotnet_major_versions.pop(-1)
            dotnet_major_versions.insert(0, poped_version)
    
    required_os_status = dict()
    for os, version in zip(required_oses, dotnet_major_versions):
        required_os_status[os] = version
    return required_os_status


def get_alternate_os_status(date_str: str) -> dict:
    '''Get the alternate OSes.

    Args:
        date_str - a string object in format `year-month-day`.
    Return: a dict object in format
        {
            `alternate_os1` = `os name 1`
            `alternate_os1` = `os name 2`
                        ...
        }
    '''
    base_status = load_json(
        os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            'baseStatus.json'
        )
    )
    alternate_oses = load_json(
        os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            'alternateOS.json'
        )
    )
    
    cycle_length = len(base_status['alternateOS'].keys())
    first_os_index = alternate_oses.index(base_status['alternateOS']['3.1'])
    week_increment = calculate_week_increment(date_str)
    if week_increment > 0:
        for _ in range(week_increment):
            first_os_index += cycle_length
    if week_increment < 0:
        for _ in range(week_increment, 0):
            first_os_index -= cycle_length

    alternate_os_status = dict()
    for i, sdk_major_version in enumerate(base_status['alternateOS'].keys()):
        alternate_os_status[sdk_major_version] = \
            alternate_oses[(first_os_index+i) % len(alternate_oses)]
    return alternate_os_status


def get_week_info(date_str: str) -> dict:
    '''Calculate monday and friday of the week which contains the given day.

    Args:
        date_str - a string object in format `year-month-day`.
    Return: a dict object in format
        {
            monday = date of monday
            friday = date of friday
        } 
    '''
    import datetime
    year, month, day = date_str.split('-')
    date_obj = datetime.datetime(
        year=int(year),
        month=int(month),
        day=int(day)
    )
    weekday = date_obj.weekday()
    monday = date_obj - datetime.timedelta(days=weekday)
    friday = monday + datetime.timedelta(days=4)
    week_info = {
        'monday': monday.strftime('%Y-%m-%d'),
        'friday': friday.strftime('%Y-%m-%d')
    }
    return week_info


def get_os_rotation(date_str):
    week_info = get_week_info(date_str)
    required_os_status = get_required_os_status(date_str)
    alternate_os_status = get_alternate_os_status(date_str)
    os_rotation = {
        'monday': week_info['monday'],
        'friday': week_info['friday'],
        'requiredOS': required_os_status,
        "alternateOS": alternate_os_status
    }
    return os_rotation


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-d', '--date',
        type=str,
        default=datetime.datetime.today().strftime('%Y-%m-%d'),
        help='string in format year-month-day'
    )
    args = parser.parse_args()
    date_str = args.date
    os_status = get_os_rotation(date_str)

    monday = os_status['monday']
    friday = os_status['friday']
    message = f'{monday} ~ {friday}\t'
    for os in os_status['requiredOS'].keys():
        sdk_major_version = os_status['requiredOS'][os]
        message += f'{os}/{sdk_major_version}\t'
    for sdk_major_version in os_status['alternateOS'].keys():
        os = os_status['alternateOS'][sdk_major_version]
        message += f'{os}/{sdk_major_version}\t'

    print(message)
