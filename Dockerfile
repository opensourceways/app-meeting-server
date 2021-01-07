FROM python:3.8-buster

MAINTAINER TommyLike<tommylikehu@gmail.com>

RUN pip install uwsgi

WORKDIR /work/app-meeting-server
COPY . /work/app-meeting-server
COPY ./deploy/fonts/simsun.ttc /usr/share/fonts

RUN cd /work/app-meeting-server && pip install -r requirements.txt && apt update && apt install -y wkhtmltopdf

EXPOSE 8080
ENTRYPOINT ["uwsgi", "--ini", "/work/app-meeting-server/deploy/production/uwsgi.ini"]
