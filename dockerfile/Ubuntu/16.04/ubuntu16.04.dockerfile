# Base images 
FROM ubuntu:16.04

# RUN
    # install required packages
RUN cd ~ && \ 
    apt-get update && apt-get install -y apt-transport-https ca-certificates wget curl && \
    echo "deb http://apt.llvm.org/xenial/ llvm-toolchain-xenial-10 main" >> /etc/apt/sources.list && \
    echo "deb-src http://apt.llvm.org/xenial/ llvm-toolchain-xenial-10 main" >> /etc/apt/sources.list && \
    wget -O - https://apt.llvm.org/llvm-snapshot.gpg.key| apt-key add - && \
    apt-get update && \
    DEBIAN_FRONTEND="noninteractive" apt-get install -y gettext git libicu-dev \
    libunwind8 lldb-10 zlib1g-dev libsqlite3-dev tar zip libffi-dev python-dev \
    make build-essential libssl-dev libbz2-dev libreadline-dev \
    llvm-10 libncurses5-dev libncursesw5-dev xz-utils tk-dev && \
    wget https://www.python.org/ftp/python/3.8.1/Python-3.8.1.tar.xz && \
    tar -xvJf Python-3.8.1.tar.xz && cd Python-3.8.1/ && \
    ./configure prefix=/usr/local/python3 && \
    make && make install && \
    mv /usr/bin/python3 /usr/bin/python3.bak && \
    ln -s /usr/local/python3/bin/python3 /usr/bin/python3 && \
    apt-get clean && rm -rf ~/Python-3.8.1.tar.xz && /bin/bash
