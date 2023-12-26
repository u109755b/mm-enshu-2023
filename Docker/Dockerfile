# Dockerfile


FROM python:3.9.0
ENV PYTHONUNBUFFERD 1
RUN mkdir /code
WORKDIR /code
COPY requirements.txt /code/
RUN pip install -r requirements.txt
RUN apt update
RUN apt upgrade -y
COPY . /code/