SHELL = /bin/sh
UNAME := $(shell uname)
PYTHON ?= python


.PHONY: help
help:
	@cat HELP

run:
	$(PYTHON) source/bouncer.py

database:
	$(PYTHON) source/model.py
