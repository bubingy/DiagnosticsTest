from SimpleRPC import *
from proxy_handler import ProxyServerStreamHandler
from redis_conn import RedisConnection
from methods import refresh_status, retrieve_task, update_status


if __name__ == '__main__':
    redis_conn = RedisConnection('redis.ini')
    handler = ProxyServerStreamHandler(redis_conn)
    handler.register_function(refresh_status)
    handler.register_function(retrieve_task)
    handler.register_function(update_status)

    server = RPCServer(handler)
    server.serve_forever('0.0.0.0', 8088)
