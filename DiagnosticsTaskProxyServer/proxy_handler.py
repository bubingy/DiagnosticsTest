from SimpleRPC import *


class ProxyServerStreamHandler(BaseServerStreamHandler):
    def __init__(self, redis_conf) -> None:
        super().__init__()
        self.redis_conf = redis_conf

    async def client_connected_cb(self,
                                  reader: StreamReader,
                                  writer: StreamWriter) -> Any:
        while True:
            try:
                message = pickle.loads(await self.receive(reader))
            except Exception as e:
                print(f'fail to receive message: {e}')
                break
            function_name = message['function_name']
            function_args = message['function_args']
            function_kwargs = message['function_kwargs']
            function_kwargs['redis_conn'] = self.redis_conf
            try:
                result = self.call(function_name, function_args, function_kwargs)
                if result is not None: self.send(writer, result)
            except Exception as e:
                print(f'fail to call {function_name}: {e}')
