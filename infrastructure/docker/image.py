from urllib import request

from infrastructure.docker.utils import get_id_from_sha, send_request


def build_image(dockerhost_ip_port: str, image_tag: str, dockerfile_uri: str) -> dict:
    query_url = (
        f'http://{dockerhost_ip_port}/v1.42/build?'
        f't={image_tag}&q=true&remote={dockerfile_uri}'
    )

    request_obj = request.Request(query_url, method='POST')
    try:
        return send_request(request_obj)
    except Exception as e:
        return Exception(f'fail to build image with {dockerfile_uri}: {e}')


def inspect_image(dockerhost_ip_port: str, image_id: str) -> dict:
    query_url = f'http://{dockerhost_ip_port}/v1.42/images/{image_id}/json'

    request_obj = request.Request(query_url)
    try:
        return send_request(request_obj)
    except Exception as e:
        return Exception(f'fail to inspect image: {e}')


def list_images(dockerhost_ip_port: str):
    query_url = (
        f'http://{dockerhost_ip_port}/v1.42/images/json?'
        f'all=true'
    )

    request_obj = request.Request(query_url)
    try:
        return send_request(request_obj)
    except Exception as e:
        return Exception(f'fail to list image: {e}')


def remove_single_image(dockerhost_ip_port: str, image_id: str):
    query_url = f'http://{dockerhost_ip_port}/v1.42/images/{image_id}'

    request_obj = request.Request(query_url, method='DELETE')
    try:
        return send_request(request_obj)
    except Exception as e:
        return Exception(f'fail to remove image {image_id}: {e}')


def remove_image_with_parents_recursively(dockerhost_ip_port: str, image_id: str):
    image_info = inspect_image(dockerhost_ip_port, image_id)
    parent_image_sha = image_info['Parent']
    if parent_image_sha != '':
        remove_single_image(dockerhost_ip_port, image_id)
        parent_image_id = get_id_from_sha(parent_image_sha)
        remove_image_with_parents_recursively(dockerhost_ip_port, parent_image_id)
    else:
        remove_single_image(dockerhost_ip_port, image_id)
