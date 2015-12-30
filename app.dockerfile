FROM tadpoles-base
MAINTAINER twneale@gmail.com

ADD . /app

CMD ["/virt/bin/python", "/app/app.py", "/.config.yml"]

