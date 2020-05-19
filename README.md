![Python package](https://github.com/podhmo/egoist/workflows/Python%20package/badge.svg) [![PyPi version](https://img.shields.io/pypi/v/egoist.svg)](https://pypi.python.org/pypi/egoist) [![](https://img.shields.io/badge/python-3.7+-blue.svg)](https://www.python.org/download/releases/3.7.0/) [![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://black.readthedocs.io/en/stable/)

# egoist

:construction: this project is under construction :construction:

- [getting started](https://github.com/podhmo/egoist/blob/master/docs/00getting-started.md)
- [ja](./docs/ja/README.md)

## installing

```console
$ pip install egoist
```

## features

- go code generation
- general code generation

### go code generation

```console
$ egoist init clikit
level:INFO	message:create .                                	name:egoist.cliL25
$ tree .
.
└── definitions.py

0 directories, 1 file
$ python definitions.py generate
[D]	create	cmd/hello
[F]	create	cmd/hello/main.go
$ go run cmd/hello/main.go -name="world"
hello world
```

🎉

### general code generation

```console
$ egoist init dirkit
level:INFO	message:create .                                	name:egoist.cliL25
$ tree .
.
├── definitions.py
└── input
    └── hello.tmpl

1 directories, 2 file
$ python definitions.py generate
[D]	create	./output
[F]	create	./output/foo.json
[F]	create	./output/bar.json
[F]	create	./output/boo.json
$ cat ./output/*.json
hello bar
hello boo
hello foo
```

✨
