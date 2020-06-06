default: clean
	mkdir -p output
	$(MAKE) generate | tee output/fullset.stdout
	ROOTDIR=output/hello-only TASK=hello $(MAKE) generate | tee output/hello-only.stdout
	ROOTDIR=output/byebye-only TASK=byebye $(MAKE) generate | tee output/byebye-only.stdout

generate: TASK ?=
generate: ROOTDIR ?= "output/fullset"
generate:
	python definitions.py generate $(TASK) --rootdir $(ROOTDIR)
.PHONY: generate

clean:
	rm -rf output
.PHONY: clean
