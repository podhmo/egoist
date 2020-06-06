# default: 00
default: 01 02 03 04 05 06

SHELL := $(shell which bash)

00:
	mkdir -p $(shell echo $@*/)dst
	python $(shell echo $@*/)main.py |& tee $(shell echo $@*/)dst/deps.dot
	which dot && dot -Tsvg $(shell echo $@*/)dst/deps.dot -O 

01:
	python $(shell echo $@*/)main.py |& tee $(shell echo $@*/)deps.output
02:
	python $(shell echo $@*/)main.py |& tee $(shell echo $@*/)deps.output
	python $(shell echo $@*/)main2.py |& tee $(shell echo $@*/)deps2.output
03:
	python $(shell echo $@*/)main.py |& tee $(shell echo $@*/)deps.output
04:
	python $(shell echo $@*/)main.py |& tee $(shell echo $@*/)deps.output
	python $(shell echo $@*/)main2.py |& tee $(shell echo $@*/)deps2.output
05:
	python $(shell echo $@*/)main.py |& tee $(shell echo $@*/)deps.output
06:
	python $(shell echo $@*/)main.py |& tee $(shell echo $@*/)deps.output
