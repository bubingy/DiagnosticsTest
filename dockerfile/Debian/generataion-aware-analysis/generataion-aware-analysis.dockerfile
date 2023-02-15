FROM debian:bullseye

RUN apt update && apt install -y clang cmake curl gettext git libicu-dev libkrb5-dev \
    liblttng-ust-dev libncurses5 libunwind8 libssl-dev \
    lldb locales locales-all python3 tar vim wget zip zlib1g-dev && \
    apt-get clean && /bin/bash 