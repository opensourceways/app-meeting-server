FROM python:3.6-alpine

MAINTAINER TommyLike<tommylikehu@gmail.com>

RUN pip install uwsgi

WORKDIR /work/app-meeting-server
COPY . /work/app-meeting-server

EXPOSE 8080
ENTRYPOINT ["uwsgi", "--ini", "/work/app-meeting-server/deploy/production/uwsgi.ini"]
