import redis
import configparser


class RedisConnection:
    def __init__(self, ini_file_path) -> None:
        config = configparser.ConfigParser()
        config.read(ini_file_path)
        self.host = config['Redis'].get('host')
        self.port = config['Redis'].getint('port')

        self.runner_table_conn = redis.Redis(
            self.host,
            self.port,
            0
        )
        self.diagnostics_task_table_conn = redis.Redis(
            self.host,
            self.port,
            1
        )
