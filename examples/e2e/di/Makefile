default: 00

SHELL := $(shell which bash)

00:
	mkdir -p $(shell echo $@*/)dst
	python $(shell echo $@*/)main.py |& tee $(shell echo $@*/)dst/deps.dot
	which dot && dot -Tsvg $(shell echo $@*/)dst/deps.dot -O 
