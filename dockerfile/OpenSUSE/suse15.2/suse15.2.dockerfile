# Base images 
FROM opensuse/leap:15.2

# RUN
    # install required packages
RUN zypper install -y curl git gzip hostname libicu \
    libunwind lldb python3 tar vim wget which zip && \
    zypper -n in -f glibc-locale && \
    zypper clean && /bin/bash