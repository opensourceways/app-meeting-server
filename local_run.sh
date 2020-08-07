#!/bin/bash

echo "checking python3"
which python3 >/dev/null 2>&1
if [[ $? -ne 0 ]]; then
  echo "python not found, exiting...."
  exit
fi
echo "checking docker"
which docker >/dev/null 2>&1
if [[ $? -ne 0 ]]; then
  echo "docker not found, exiting...."
  exit
fi

pip3 install virtualenv
virtualenv meetingserverenv
source meetingserverenv/bin/activate
pip install -r requirements.txt
echo "checking mysql container"
docker ps | grep meeting-mysql-server >/dev/null 2>&1
if [[ $? -eq 0 ]]; then
  echo "container will be restarted"
  docker stop meeting-mysql-server | xargs docker rm
fi
docker run --name meeting-mysql-server -p 3306:3306 -e MYSQL_ROOT_PASSWORD=123456 -e MYSQL_DATABASE=meetings -d mysql:8.0
