# Base images 
FROM ubuntu:18.04

# RUN
    # install required packages
RUN cd ~ && \ 
    apt-get update && apt-get install -y apt-transport-https ca-certificates gnupg2 wget && \
    echo "deb http://apt.llvm.org/bionic/ llvm-toolchain-bionic-10 main" >> /etc/apt/sources.list && \
    echo "deb-src http://apt.llvm.org/bionic/ llvm-toolchain-bionic-10 main" >> /etc/apt/sources.list && \
    wget -O llvm-snapshot.gpg.key https://apt.llvm.org/llvm-snapshot.gpg.key && \
    apt-key add llvm-snapshot.gpg.key && apt-get update && rm -rf llvm-snapshot.gpg.key && \
    apt-get update && \
    DEBIAN_FRONTEND="noninteractive" apt install -y curl gettext git libicu-dev \
     libunwind8 lldb-10 python3 tar vim wget zip && \
    apt-get clean && /bin/bash
