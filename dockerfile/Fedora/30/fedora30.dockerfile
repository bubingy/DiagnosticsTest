# Base images 
FROM fedora:30

RUN dnf install -y curl findutils git libicu libunwind \
    lldb-devel python3 tar vim wget which zip && \
    dnf clean all && /bin/bash
