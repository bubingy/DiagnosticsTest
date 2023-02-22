import json
from urllib import request


def send_request(req: request.Request) -> dict:
    response = request.urlopen(req)
    response_content = response.read().decode('utf-8')
    return json.loads(response_content)
    

def get_id_from_sha(sha: str) -> str:
    return sha.split(':')[1][:16]


def generate_container_config(**kwargs):
    config = {}
    