# default: 00
default: 01 02 03

SHELL := $(shell which bash)

00:
	mkdir -p $(shell echo $@*/)dst
	python $(shell echo $@*/)main.py |& tee $(shell echo $@*/)dst/deps.dot
	which dot && dot -Tsvg $(shell echo $@*/)dst/deps.dot -O 

01:
	python $(shell echo $@*/)main.py |& tee $(shell echo $@*/)deps.output
02:
	python $(shell echo $@*/)main.py |& tee $(shell echo $@*/)deps.output
03:
	python $(shell echo $@*/)main.py |& tee $(shell echo $@*/)deps.output
