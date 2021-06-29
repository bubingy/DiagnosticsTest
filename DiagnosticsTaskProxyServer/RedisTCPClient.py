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

    def receive_response(self) -> Any:
        type_flag = self.conn.recv(1)
        if type_flag == b'+':
            content = b''
            while b'\r\n' != content[-2:]:
                content += self.conn.recv(1)
            return content.decode(self.coding).strip('+\r\n')

        elif type_flag == b'-':
            content = b''
            while b'\r\n' != content[-2:]:
                content += self.conn.recv(1)
            return content.decode(self.coding).strip('-\r\n')

        elif type_flag == b':':
            content = b''
            while b'\r\n' != content[-2:]:
                content += self.conn.recv(1)
            return int(content.decode(self.coding).strip(':\r\n'))

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

        elif type_flag == b'*':
            array_size = b''
            while b'\r\n' != array_size[-2:]:
                array_size += self.conn.recv(1)
            array_size = int(array_size.decode(self.coding).strip('\r\n'))
            if array_size == -1: return None

            array = list()
            if array_size == 0: return array

            for _ in range(array_size):
                array.append(self.receive_response())
            return array

        else:
            return None

    def run_command(self, command: str) -> Any:
        result = None
        try:
            self.conn.send(f'{command}\r\n'.encode('utf-8'))
            result = self.receive_response()
        except Exception as e:
            print(e)
        return result