SHELL = /bin/sh
UNAME := $(shell uname)
PYTHON ?= python
SSH_HOST=
SSH_PORT=
SSH_USER=
SSH_TARGET_DIR=


.PHONY: help
help:
	@cat HELP

.PHONY: run
run:
	$(PYTHON) source/bouncer.py

.PHONY: database
database:
	$(PYTHON) source/model.py

.PHONY: rsync_push
rsync_push:
	rsync -ar --progress "$$(pwd)/" "$(SSH_USER)@$(SSH_HOST):$(SSH_TARGET_DIR)" --filter=':- .gitignore'

.PHONY: remote_restart
remote_restart:
	ssh "$(SSH_USER)@$(SSH_HOST)" 'systemctl restart bouncer'
