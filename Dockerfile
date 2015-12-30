FROM ubuntu:trusty
MAINTAINER twneale@gmail.com

RUN apt-get update && apt-get upgrade -y

RUN apt-get install -qyy \
    -o APT::Install-Recommends=false -o APT::Install-Suggests=false \
    python-virtualenv python3.4-dev python3-setuptools \
    python3-pip xvfb firefox python3-lxml 

RUN pip3 install selenium xvfbwrapper pyyaml requests

WORKDIR /app
ADD "py/*" /app/
CMD ["python3.4", "/app/app.py"]
