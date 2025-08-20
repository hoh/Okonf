FROM docker.io/library/debian:trixie

RUN apt-get update && apt-get -y upgrade && apt-get -y install \
    --no-install-recommends \
    python3-pip python3-venv sudo git openssh-server

RUN python3 -m venv /opt/venv
RUN /opt/venv/bin/pip install hatch

COPY . /opt/okonf

WORKDIR /opt/okonf

CMD ["/opt/venv/bin/hatch", "run", "dev:test"]
