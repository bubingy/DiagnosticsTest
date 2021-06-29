import configparser

from RedisTCPClient import RedisTCPClient


class RedisConnection:
    def __init__(self, ini_file_path) -> None:
        config = configparser.ConfigParser()
        config.read(ini_file_path)
        self.host = config['Redis'].get('host')
        self.port = config['Redis'].getint('port')

        self.conn = RedisTCPClient(self.host, self.port)
