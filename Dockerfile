FROM debian:stretch

RUN apt-get update && apt-get -y upgrade && apt-get -y install virtualenv sudo
RUN virtualenv -p python3 /opt/venv

COPY requirements /opt/requirements
RUN /opt/venv/bin/pip install -r /opt/requirements/tests.txt
RUN /opt/venv/bin/pip install -r /opt/requirements/latest.txt

COPY okonf /opt/okonf
COPY tests /opt/tests
COPY run_tests.sh /opt/run_tests.sh

ENV PYTHONPATH="/opt/"
WORKDIR /opt

CMD ["/opt/venv/bin/pytest", "--cov=okonf", "--flakes", "--pep8", "tests", "okonf"]
