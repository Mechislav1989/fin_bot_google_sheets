FROM ubuntu:latest

MAINTAINER Mechislav Yastremskyi 'ysatrianim@gmail.com'

COPY ./requirements.txt /Flask_exmpl/requirements.txt

WORKDIR /Flask_exmpl

RUN apt-get update -y

RUN apt-get install -y python3

RUN apt-get install -y python3-pip

RUN pip install -r requirements.txt

COPY . /Flask_exmpl