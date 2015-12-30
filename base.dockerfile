FROM ubuntu:trusty
MAINTAINER twneale@gmail.com

RUN apt-get update

RUN apt-get install -qyy \
    -o APT::Install-Recommends=false -o APT::Install-Suggests=false \
    python-virtualenv python3.4-dev python3-setuptools \
    python3-pip xvfb firefox

RUN virtualenv -p /usr/bin/python3.4 /virt
RUN /virt/bin/pip install --upgrade pip

ADD requirements.txt /app/requirements.txt
RUN /virt/bin/pip install -r /app/requirements.txt
