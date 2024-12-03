FROM python:3.10.15-slim
# FROM artifactory.oneadr.net/remote-docker-hub/python:3.10.15-slim

RUN apt update

ADD pip.conf /etc/pip.conf
WORKDIR /opt/app
COPY requirements.txt /opt/app/requirements.txt

RUN pip install -r requirements.txt

