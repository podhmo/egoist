makegen:
	rm -f _gen.mk && touch _gen.mk
	python definitions.py makegen | tee _gen.mk

graphgen:
	python definitions.py graphgen | tee graph.dot

do: makegen graphgen

include _setup.mk
include _gen.mk

# .DEFAULT_GOAL = default
.DEFAULT_GOAL = do
