# Base images 
FROM centos:8

# RUN
    # install required packages
RUN yum install -y vim wget curl epel-release && \
    yum install -y git libicu libunwind lldb python3 tar which zip && \
    yum clean all && /bin/bash 
    