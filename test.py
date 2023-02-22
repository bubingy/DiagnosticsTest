from infrastructure.docker import container

image_id = '81b958faac724992e164d3789ca7e19e8538ae91c5fe29e71909f27d0808b046'

container_info = container.create_container(
    '172.16.195.99:2345',
    'alpine3.15:diag',
    command=['/bin/bash', '-c', 'cd ~ && touch test.txt && echo \'hello world\' > test.txt'],
    cap_add=['SYS_PTRACE'],
    name='alpine3.15diag',
    remove=True,
    security_opt =['seccomp=unconfined'],
    volumes=['/home/vbibu/docker-mount/alpine3.15diag:/root']
)

print(container_info)

