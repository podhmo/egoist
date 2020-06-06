default:
	$(MAKE) clean
	$(MAKE) generate

generate:
	python definitions.py generate - scan --out=scan.output

## this is bad. configuration only once.
# python definitions.py scan --out=scan.output - generate

.PHONY: generate

clean:
	rm -rf cmd
.PHONY: clean
