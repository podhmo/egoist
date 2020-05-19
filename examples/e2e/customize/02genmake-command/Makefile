default: output/x.yaml output/x.go output/y.go

include _setup.mk

output/x.yaml: _tools/gen.py _tools/x-yaml.j2 input/x.csv
	python $< x-yaml _tools/x-yaml.j2 input/x.csv > $@
output/x.go: _tools/gen.py _tools/x-go.j2 input/x.csv
	python $< x-go _tools/x-go.j2 input/x.csv > $@

output/y.go: _tools/gen.py _tools/y-go.j2 input/root.yaml
	python $< y-go _tools/y-go.j2 input/root.yaml > $@

clean:
	rm -rf _tools output
	mkdir -p _tools output

