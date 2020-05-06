default:
	$(MAKE) clean
	$(MAKE) generate

generate:
	python definitions.py generate
.PHONY: generate

clean:
	rm -rf cmd
.PHONY: clean
