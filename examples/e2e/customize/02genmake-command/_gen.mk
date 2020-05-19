DEP ?= output/x.yaml output/x.go output/y.go
PRE ?= .pre/output__x.yaml .pre/output__x.go .pre/output__y.go
CONT ?= PRE=$< DEP="" $(MAKE) _gen

# goal task
default:
	CONT="exit 0" $(MAKE) _gen

_gen: $(DEP)
	@echo '**' $(PRE) '**' > /dev/stderr
	python definitions.py $(shell { $(foreach p,$(PRE),cat $(p);) } | sort | uniq | tr '\n' ' ')

.pre/output__x.yaml: .pre input/x.csv _tools/x-yaml.j2 _tools/gen.py
	echo "generate x -"> $@
.pre/output__x.go: .pre input/x.csv _tools/x-go.j2 _tools/gen.py
	echo "generate x -"> $@
.pre/output__y.go: .pre input/root.yaml _tools/y-go.j2 _tools/gen.py
	echo "generate y_go -"> $@

output/x.yaml: .pre/output__x.yaml
	@$(CONT)
output/x.go: .pre/output__x.go
	@$(CONT)
output/y.go: .pre/output__y.go
	@$(CONT)

.pre:
	mkdir -p $@
