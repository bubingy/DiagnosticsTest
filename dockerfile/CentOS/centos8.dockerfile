# Base images 
FROM centos:8

RUN cd /etc/yum.repos.d/ && sed -i 's/mirrorlist/#mirrorlist/g' /etc/yum.repos.d/CentOS-* && \
    sed -i 's|#baseurl=http://mirror.centos.org|baseurl=http://vault.centos.org|g' /etc/yum.repos.d/CentOS-*

RUN yum install -y vim wget curl epel-release && \
    yum install -y git libicu libunwind lldb python3 tar which zip && \
    yum clean all && /bin/bash 
    