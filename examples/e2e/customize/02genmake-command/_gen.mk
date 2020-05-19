DEP ?= output/x.yaml output/x.go output/y.go
PRE ?= .pre/output__x.yaml .pre/output__x.go .pre/output__y.go

CONT ?= PRE=$< DEP="" $(MAKE) _gen
BULK_ACTION = .pre/bulk.action

# goal task
default:
	@CONT="exit 0" $(MAKE) _gen

_gen: .pre $(DEP)
	@echo '**' $(PRE) '**' > /dev/stderr
	( $(foreach p,$(PRE),{ test $(p) -nt $(subst __,/,$(patsubst .pre/%,%,$(p))) && cat $(p); }; ) ) | sort | uniq > $(BULK_ACTION) || exit 0
	test -n "$$(cat $(BULK_ACTION))" && python definitions.py $$(cat $(BULK_ACTION) | tr '\n' ' ') || exit 0

# .pre files (sentinel)
.pre/output__x.yaml: _tools/x-yaml.j2 input/x.csv _tools/gen.py
	echo "generate x -" > $@
.pre/output__x.go: input/x.csv _tools/gen.py _tools/x-go.j2
	echo "generate x -" > $@
.pre/output__y.go: _tools/gen.py input/root.yaml _tools/y-go.j2
	echo "generate y_go -" > $@

# actual dependencies
output/x.yaml: .pre/output__x.yaml
	@$(CONT)
output/x.go: .pre/output__x.go
	@$(CONT)
output/y.go: .pre/output__y.go
	@$(CONT)

.pre:
	mkdir -p $@
