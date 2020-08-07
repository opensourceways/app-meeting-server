.EXPORT_ALL_VARIABLES:
SHELL := /bin/bash

dev-env:
	./local_run.sh

run-server:
	source meetingserverenv/bin/activate
	python3 manage.py runserver
