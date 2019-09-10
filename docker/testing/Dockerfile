FROM python:3.6.8-slim-jessie
ENV PYTHONUNBUFFERED 1

RUN apt-get update
RUN apt-get install -y build-essential
RUN apt-get install -y cmake
RUN apt-get install -y python3-dev
RUN apt-get install -y mc
RUN apt-get install -y nano

RUN pip3 install pip --upgrade
RUN pip3 install virtualenv

RUN mkdir /code
WORKDIR /code
ADD pytest.ini /code/pytest.ini
ADD runtests.py /code/runtests.py
ADD requirements.txt /code/requirements.txt
ADD requirements/ /code/requirements/
ADD scripts/ /code/scripts/
ADD docker/ /code/docker/
RUN pip3 install -r /code/requirements.txt
#COPY ./docker /code/docker/
