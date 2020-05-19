genmake:
	rm -f _gen.mk && touch _gen.mk
	python definitions.py genmake | tee _gen.mk

include _setup.mk
include _gen.mk

.DEFAULT_GOAL = default
