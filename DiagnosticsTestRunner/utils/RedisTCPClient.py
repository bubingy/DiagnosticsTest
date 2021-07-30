# coding=utf-8

import socket
from typing import Any


class RedisTCPClient:
    def __init__(self,
                 host: str,
                 port: int,
                 buffer_size: int=4096,
                 coding: str='utf-8') -> None:
        self.host, self.port = host, port
        self.buffer_size = buffer_size
        self.coding = coding
        self.conn = socket.socket()
        self.conn.connect((self.host, self.port))

    def __receive_response(self) -> Any:
        '''Receive and parse response.
        
        For more details about Redis Serialization Protocol,
        please visit https://redis.io/topics/protocol
        '''
        # first character indicates data type.
        type_flag = self.conn.recv(1)
        # For Simple Strings the first byte of the reply is "+"
        if type_flag == b'+':
            content = b''
            while b'\r\n' != content[-2:]:
                content += self.conn.recv(1)
            return content.decode(self.coding).strip('+\r\n')

        # For Errors the first byte of the reply is "-"
        elif type_flag == b'-':
            content = b''
            while b'\r\n' != content[-2:]:
                content += self.conn.recv(1)
            return content.decode(self.coding).strip('-\r\n')

        # For Integers the first byte of the reply is ":"
        elif type_flag == b':':
            content = b''
            while b'\r\n' != content[-2:]:
                content += self.conn.recv(1)
            return int(content.decode(self.coding).strip(':\r\n'))

        # For Bulk Strings the first byte of the reply is "$"
        elif type_flag == b'$':
            string_size = b''
            while b'\r\n' != string_size[-2:]:
                string_size += self.conn.recv(1)

            string_size = int(string_size.decode(self.coding).strip('\r\n'))
            if string_size == -1: return None

            content = b''
            while string_size > self.buffer_size:
                buffer_size = min(string_size, self.buffer_size)
                content += self.conn.recv(buffer_size)
                string_size -= buffer_size

            while b'\r\n' != content[-2:]:
                content += self.conn.recv(1)
            return content.decode(self.coding).strip('\r\n')

        # For Arrays the first byte of the reply is "*"
        elif type_flag == b'*':
            array_size = b''
            while b'\r\n' != array_size[-2:]:
                array_size += self.conn.recv(1)
            array_size = int(array_size.decode(self.coding).strip('\r\n'))
            if array_size == -1: return None

            array = list()
            if array_size == 0: return array

            # To handle with arrays of arrays scenario,
            # call `receive_response()` recursively.
            for _ in range(array_size):
                array.append(self.__receive_response())
            return array

        else:
            return None

    def run_command(self, command: str) -> Any:
        '''Execute redis command.

        :param command: redis command
        :return: result.
        '''
        result = None
        try:
            self.conn.send(f'{command}\r\n'.encode('utf-8'))
            result = self.__receive_response()
        except Exception as e:
            print(e)
        return result

    def run_commands(self, commands: list) -> list:
        '''Allow the execution of a group of commands in a single step.

        :param command: a list of redis command
        :return: result.
        '''
        result = None
        try:
            self.run_command(f'MULTI\r\n')
            for command in commands:
                self.run_command(f'{command}\r\n')
            result = self.run_command(f'EXEC\r\n')
        except Exception as e:
            print(e)
        return result