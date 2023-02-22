from urllib import request, parse


def create_container(host_ip_port, image, command=None, hostname=None, user=None,
                         detach=False, stdin_open=False, tty=False, ports=None,
                         environment=None, volumes=None,
                         network_disabled=False, name=None, entrypoint=None,
                         working_dir=None, domainname=None, host_config=None,
                         mac_address=None, labels=None, stop_signal=None,
                         networking_config=None, healthcheck=None,
                         stop_timeout=None, runtime=None,
                         use_config_proxy=True, platform=None):
    if isinstance(volumes, str):
        volumes = [volumes, ]

    config = create_container_config(
        host_ip_port, image, command, hostname, user, detach, stdin_open, tty,
        ports, environment, volumes,
        network_disabled, entrypoint, working_dir, domainname,
        host_config, mac_address, labels,
        stop_signal, networking_config, healthcheck,
        stop_timeout, runtime
    )
    return create_container_from_config(host_ip_port, config, name)


def create_container_config(*args, **kwargs):
    return ContainerConfig('1.42', *args, **kwargs)


def create_container_from_config(host_ip_port:str, config, name=None):
    url = f'{host_ip_port}/v1.42/containers/create?name={name}'
    encoded_data = parse.urlencode(config).encode('utf-8')
    request_obj = request.Request(url, data=encoded_data, method='POST')
    
    return send_request(request_obj)


def run_container(host_ip_port, image, command=None, stdout=True, stderr=False, remove=False, **kwargs):
    container = create_container(host_ip_port, image, command=command, **kwargs)
    container.start()