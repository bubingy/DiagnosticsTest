# Base images 
FROM ubuntu:20.04

# RUN
    # install required packages
RUN apt update && \
    DEBIAN_FRONTEND="noninteractive" apt install -y  curl git libicu-dev lldb-10 \
        libunwind8 python3 vim tar wget zip && /bin/bash
