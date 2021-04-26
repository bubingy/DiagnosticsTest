FROM alpine:3.9

RUN sed -i 's/http/https/g' /etc/apk/repositories && \
    apk update && \
    apk add --no-cache autoconf bash curl coreutils gettext git icu-dev \
    krb5-dev libunwind-dev openssl-dev python3 wget which vim && \
    rm -rf /var/cache/apk/* && /bin/bash