from redis_conn import RedisConnection


def refresh_status(client_info: dict,
                   redis_conn: RedisConnection=None) -> None:
    '''refresh runner's status.

    :param client_info: info of runner. 
    :param redis_conn: connection instance of redis.
    '''
    runner_name = client_info['runner_name']
    runner_host = client_info['host_name']
    redis_conn.conn.run_command('SELECT 0')
    runner_status = redis_conn.conn.run_command(
        f'GET {runner_name}@{runner_host}'
    )

    if runner_status is None: runner_status = 'idling'

    runner_status = redis_conn.conn.run_command(
        f'SET {runner_name}@{runner_host} {runner_status} EX 10'
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

    redis_conn.conn.run_command('SELECT 0')
    runner_status = redis_conn.conn.run_command(
        f'SET {runner_name}@{runner_host} {runner_status} EX 10'
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
    redis_conn.conn.run_command('SELECT 0')
    keys = redis_conn.conn.run_command('KEYS *')
    for key in keys:
        if runner_host not in key: continue
        runner_status = redis_conn.conn.run_command(
            f'GET {runner_name}@{runner_host}'
        )
        if runner_status == 'idling': continue
        return None
    
    
    redis_conn.conn.run_command('SELECT 1')
    if redis_conn.conn.run_command(f'LLEN {runner_name}') == 0: return None

    plan = redis_conn.conn.run_command(f'LPOP {runner_name}')
    return plan
 