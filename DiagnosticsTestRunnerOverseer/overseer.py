# coding=utf-8

from threading import Thread

from bottle import Bottle, run

from service import retrieve_task
from utils import Result

app = Bottle()

@app.route('/work', method='GET')
def work():
    '''Start to process tasks in rabbitmq.

    Retrieve task from rabbitmq and assign it to runner until the queue is empty.
    '''
    try:
        t = Thread(target=retrieve_task)
        t.start()
        result = Result(0, 'start working', None)
    except Exception as e:
        result = Result(-1, 'fail to start', e)
    return result

run(app, host='localhost', port=8080)