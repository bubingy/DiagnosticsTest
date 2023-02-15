# Base images 
FROM debian:bullseye

# RUN
    # install required packages
RUN apt update && apt install -y binutils curl gettext git libicu-dev libncurses5 \
    libcap2 libopencsd0 libslang2 libunwind8 linux-base linux-perf linux-perf-5.10 \
    lttng-tools liblttng-ust-dev locales locales-all python3 tar vim wget zip && \
    apt-get clean && /bin/bash 