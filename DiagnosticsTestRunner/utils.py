# coding=utf-8

import json

class DictFromFile:
    def __init__(self, file_path) -> None:
        self.file_path = file_path
        with open(file_path, 'r') as reader:
            self.content = json.loads(reader.read())
