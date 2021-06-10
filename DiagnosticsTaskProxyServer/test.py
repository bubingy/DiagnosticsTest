import redis


conn = redis.Redis(
    '10.20.10.158',
    6379,
    1
)

print(conn.get('test1@test1'))