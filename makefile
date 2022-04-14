SHELL = /bin/sh
UNAME := $(shell uname)
PYTHON ?= python


.PHONY: help
help:
	@cat HELP

run:
	$(PYTHON) source/linkbot.py
