default:
	$(MAKE) clean
	$(MAKE) generate

generate:
	python definitions.py scan --out=scan.output
.PHONY: generate

clean:
	rm -rf cmd
.PHONY: clean
