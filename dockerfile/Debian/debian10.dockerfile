# Base images 
FROM debian:buster

# RUN
    # install required packages
RUN apt update && apt install -y curl gettext git libicu-dev libncurses5 \
    libunwind8 lldb locales locales-all python3 tar vim wget zip && \
    apt-get clean && /bin/bash 