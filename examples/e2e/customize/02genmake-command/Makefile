default: output/x.yaml output/x.go output/y.go

genmake:
	python definitions.py genmake | tee _gen.mk

include _setup.mk
include _gen.mk
