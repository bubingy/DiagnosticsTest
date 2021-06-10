from SimpleRPC import *
from proxy_handler import ProxyServerStreamHandler
from redis_conn import RedisConnection
from methods import refresh_status, retrieve_task


if __name__ == '__main__':
    redis_conf = RedisConnection('redis.ini')
    handler = ProxyServerStreamHandler(redis_conf)
    handler.register_function(refresh_status)
    handler.register_function(retrieve_task)

    server = RPCServer(handler)
    server.serve_forever('0.0.0.0', 8088)
