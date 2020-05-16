default:
	$(MAKE) clean
	$(MAKE) scan
	$(MAKE) generate

generate:
	python definitions.py generate
scan:
	python definitions.py scan | tee scan.output
.PHONY: generate

clean:
	rm -rf cmd
.PHONY: clean
