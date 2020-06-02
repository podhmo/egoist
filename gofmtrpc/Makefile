run: ADDR ?= :9999
run: gen
	go run cmd/gofmtrpc/main.go -addr $(ADDR)

gen:
	go generate ./
	python definitions.py generate

test-smd:
	http --pretty=format --json :9999 smd==1 | tee _data/smd.json
test-flight:
	echo '{"id": 1, "jsonrpc": "2.0", "method": "format", "params": {"code": $(shell cat _data/hello.go | python -c 'import json; import sys; print(repr(json.dumps(sys.stdin.read()))[1:-1])' )}}' | http -b --json POST :9999/ | jq .result -r | tee _data/hello.formatted.go
