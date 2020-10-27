SHELL := /bin/bash
PWD := $(shell pwd)
default: build

all:

docker-image:
	docker build -f ./backup-server/Dockerfile -t "backup-server:latest" .
	docker build -f ./company-server/Dockerfile -t "company-server:latest" .
	docker build -f ./backuper-worker/Dockerfile -t "backuper-worker:latest" .
.PHONY: docker-image

docker-compose-up: docker-image
	docker-compose -f docker-compose-dev.yaml up -d --build
.PHONY: docker-compose-up

docker-compose-down:
	sudo rm -r ./volumes/backupers/*
	sudo rm -r ./volumes/backup_server
	docker-compose -f docker-compose-dev.yaml stop -t 1
	docker-compose -f docker-compose-dev.yaml down
.PHONY: docker-compose-down

docker-compose-logs:
	docker-compose -f docker-compose-dev.yaml logs -f
.PHONY: docker-compose-logs
