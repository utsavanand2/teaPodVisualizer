FROM resin/raspberrypi3-alpine:3.6

RUN apk update && \
    apk add --no-cache python3-dev && \
    python3 -m ensurepip && \
    rm -r /usr/lib/python*/ensurepip && \
    pip3 install --upgrade pip setuptools && \
    if [ ! -e /usr/bin/pip ]; then ln -s pip3 /usr/bin/pip ; fi && \
    if [[ ! -e /usr/bin/python ]]; then ln -sf /usr/bin/python3 /usr/bin/python; fi && \
    rm -r /root/.cache

RUN apk add --virtual build-dependencies \
    build-base \
    gcc \
    make \
    openssl \
    bsd-compat-headers \
    linux-headers \
    wget \
    git

RUN mkdir -p /ledctl/src
COPY requirements.txt /ledctl
WORKDIR /ledctl

RUN pip install -r requirements.txt && \
    apk del build-dependencies

COPY ./src /ledctl/src
ENTRYPOINT [ "python3", "-u", "src/led.py" ]