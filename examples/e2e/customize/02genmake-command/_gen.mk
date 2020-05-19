output/x.yaml: _tools/gen.py input/x.csv _tools/x-yaml.j2
	python definitions.py generate x

output/x.go: _tools/gen.py input/x.csv _tools/x-go.j2
	python definitions.py generate x

output/y.go: _tools/gen.py _tools/y-go.j2 input/root.yaml
	python definitions.py generate y_go
