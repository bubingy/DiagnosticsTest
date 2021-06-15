import sys
import pickle
import asyncio
from typing import Any
from asyncio.streams import StreamReader, StreamWriter


##############################
#          Handler           #
##############################
'''
A message should be in following format:
PART 1. Size of body
The size of this part is fixed: 8 bytes.
It indicates the size of the entity-body.

PART 2. Body
Body can be converted to a json format object(to be determined).
It contains following keys:  
* function_name - name of function
* function_args - args for function
* function_kwargs - kwargs for function
'''
class BaseStreamHandler:
    '''BasicStreamHandler class.

    '''
    def __init__(self) -> None:
        self._registered_functions = dict()
        self._registered_instances = dict()
    
    def register_function(self, fun) -> None:
        '''Register a function for calling.

        :param fun: a callable object.
        '''
        if fun.__name__ in self._registered_functions.keys():
            raise 'function already registered.'
        self._registered_functions[fun.__name__] = fun.__module__
    
    def register_instance(self, instance: object) -> None:
        '''Register a class instance for calling.

        :param instance: a class instance.
        '''
        instance_name = get_object_name(instance.__module__, instance)
        if instance_name in self._registered_instances.keys():
            raise 'instance already registered.'
        self._registered_instances[instance_name] = instance.__module__

    @classmethod
    async def receive(self, reader: StreamReader) -> bytes:
        '''Receive data.
            
        :param reader: a StreamReader object.
        :return: retrieved bytes.
        '''
        data = b''
        try:
            body_size = int.from_bytes(await reader.readexactly(8), 'big')
        except Exception as e:
            print(e)
            return None
        while body_size > 0:
            buffer_size = min(4096, body_size)
            buffer = await reader.readexactly(buffer_size)
            data += buffer
            body_size -= buffer_size
        return data

    @classmethod
    def send(self, writer: StreamWriter, data: Any) -> None:
        '''Send data.
        
        :param writer: a StreamWriter object.
        :param data: data to send.
        '''
        message = b''
        try:
            body = pickle.dumps(data)
        except Exception as e:
            print(f'fail to dump message: {e}')
            return
        body_size = len(body)
        message += body_size.to_bytes(8, 'big')
        message += body
        writer.write(message)

    def call(self,
             function_name: str,
             function_args: tuple=tuple(),
             function_kwargs: dict=dict()) -> Any:
        if '.' in function_name:
            function_call_path = function_name.split('.')
            if len(function_call_path) != 2: return

            instance_name = function_call_path[0]
            function_name = function_call_path[1]
            try:
                instance_module = sys.modules[self._registered_instances[instance_name]]
                method_to_call = getattr(
                    instance_module.__getattribute__(instance_name),
                    function_name
                )
                returned_value = method_to_call(
                    *function_args,
                    **function_kwargs
                )
            except Exception as e:
                returned_value = None
                print(f'fail to call {instance_name}.{function_name}: {e}')
        else:
            try:
                method_to_call = getattr(
                    sys.modules[self._registered_functions[function_name]], 
                    function_name
                )
                returned_value = method_to_call(
                    *function_args,
                    **function_kwargs
                )
            except Exception as e:
                returned_value = None
                print(f'fail to call {function_name}: {e}')
        return returned_value


class BaseServerStreamHandler(BaseStreamHandler):
    '''BaseServerStreamHandler class

    Please implement following method by yourself:
        client_connected_cb(self,
                            reader: StreamReader,
                            writer: StreamWriter) -> Any
    '''
    def __init__(self) -> None:
        super().__init__()

    async def client_connected_cb(self,
                                  reader: StreamReader,
                                  writer: StreamWriter) -> Any:
        '''This method will be called if a connection is established. 

        :param reader: a StreamReader object.
        :param writer: a StreamWriter object.
        '''
        pass


##############################
#           Server           #
##############################
class RPCServer:
    '''A basic async RPC server.

    '''
    def __init__(self, handler: BaseServerStreamHandler) -> None:
        '''Constructor.

        :param handler: a BaseServerStreamHandler object which 
            implement client_connected_cb method.
        '''
        self.handler = handler

    def serve_forever(self,
                      host: str,
                      port: int,
                      **kwargs) -> None:
        '''Start the server.
        
        :param host: host ip.
        :param port: port to listen.
        '''
        # get event loop
        loop = kwargs.get('loop')
        if loop is not None: 
            self.event_loop = loop
            asyncio.set_event_loop()
        else:
            self.event_loop = asyncio.get_event_loop()

        # create async TCP server coroutine 
        self.server_coro = asyncio.start_server(
            self.handler.client_connected_cb,
            host,
            port,
            **kwargs
        )
        self.event_loop.run_until_complete(self.server_coro)
        self.event_loop.run_forever()


##############################
#           Utils            #
##############################
def get_object_name(module_name: str, object: Any) -> str:
    '''Get name of given object.

    :param module_name: name of module where the object is defined.
    :param object: the object.
    :return: name of given object.
    '''
    object_id = id(object)
    for obj_name in dir(sys.modules[module_name]):
        if id(sys.modules[module_name].__getattribute__(obj_name)) == object_id:
            return obj_name
    return None
