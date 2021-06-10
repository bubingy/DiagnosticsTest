from redis_conn import RedisConnection


def refresh_status(client_info: dict,
                   redis_conn: RedisConnection=None) -> None:
    '''refresh runner's status.

    :param client_info: info of runner. 
    :param redis_conn: connection instance of redis.
    '''
    runner_name = client_info['runner_name']
    runner_host = client_info['host_name']
    runner_status = redis_conn.runner_table_conn.get(
        f'{runner_name}@{runner_host}'
    )

    if runner_status is None: runner_status = b'idling'
    runner_status = runner_status.decode('utf-8')

    redis_conn.runner_table_conn.set(
        f'{runner_name}@{runner_host}',
        runner_status,
        ex=10
    )


def update_status(client_info: dict,
                  runner_status: str,
                  redis_conn: RedisConnection=None) -> None:
    '''update runner's status.

    :param client_info: info of runner.
    :param runner_status: status of runner.
    :param redis_conn: connection instance of redis.
    '''
    runner_name = client_info['runner_name']
    runner_host = client_info['host_name']
    redis_conn.runner_table_conn.set(
        f'{runner_name}@{runner_host}',
        runner_status,
        ex=10
    )


def retrieve_task(client_info: dict,
                  redis_conn: RedisConnection=None) -> dict:
    '''Retrieve task from redis.

    :param client_info: info of runner.
    :param redis_conn: connection instance of redis.
    '''
    runner_name = client_info['runner_name']
    runner_host = client_info['host_name']

    # check if the host is working.
    for key in redis_conn.runner_table_conn.scan_iter():
        if runner_host not in key: continue
        if redis_conn.runner_table_conn.get(key) == b'idling': continue
        return None
    
    if redis_conn.task_table_conn.llen() == 0: return None
    plan = redis_conn.task_table_conn.lpop(runner_name)
    update_status(client_info, 'running', redis_conn)
    return plan
 