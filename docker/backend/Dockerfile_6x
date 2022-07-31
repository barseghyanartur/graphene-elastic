FROM python:3.9-slim-bullseye
ENV PYTHONUNBUFFERED 1

RUN apt-get update
RUN apt-get install -y build-essential
RUN apt-get install -y cmake
RUN apt-get install -y python3-dev
RUN apt-get install -y mc
RUN apt-get install -y nano

RUN pip3 install pip --upgrade
RUN pip3 install virtualenv
RUN pip3 install pip-tools

RUN mkdir /code
WORKDIR /code
COPY . /code/
#RUN pip-compile /code/requirements/testing_7x.in
#RUN pip3 install -r /code/requirements/testing_7x.txt
