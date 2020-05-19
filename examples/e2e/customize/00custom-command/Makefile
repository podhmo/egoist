SHELL := $(shell which bash)
NAME := hello

default:
	python definitions.py $(NAME) |& tee $(NAME).output
