# getting started

:warning: The API design is a prototype and may change in the future.

## init and run

scaffold (init)

```console
$ mkdir sandbox && cd sandbox
$ egoist init
$ tree
.
└── definitions.py

0 directories, 1 file
```

generate `cmd/{hello}/main.go` by definitions.py. (this is generated [main.go](../examples/e2e/generate-clikit/00simple/cmd/hello/main.go))

```console
$ python definitions.py generate
[D]     create  cmd/hello
[F]     create  cmd/hello/main.go
```

run

```console
$ tree
.
├── cmd
│   └── hello
│       └── main.go
└── definitions.py

2 directories, 2 files

$ go run cmd/hello/main.go -h
hello - hello message

Usage:
  -name string
        -
exit status 1

$ go run cmd/hello/main.go -name foo
hello foo
```

more details is [here](../examples/e2e/generate-clikit/00simple).

### defnitions.py

definitions.py

```python
from egoist.app import App, SettingsDict

settings: SettingsDict = {"rootdir": "cmd/", "here": __file__}
app = App(settings)

app.include("egoist.directives.define_cli")


@app.define_cli("egoist.generators.clikit:walk")
def hello(*, name: str) -> None:
    """hello message"""
    from egoist.generators.clikit import runtime, clikit

    with runtime.generate(clikit):
        runtime.printf("hello %s\n", name)


if __name__ == "__main__":
    app.run()
```

## using other package's function

if you want to calling other package's function. you can use `m.import_()`.

definitions.py

```python
from egoist.app import App, SettingsDict

settings: SettingsDict = {"rootdir": "cmd/", "here": __file__}
app = App(settings)

app.include("egoist.directives.define_cli")


@app.define_cli("egoist.generators.clikit:walk")
def hello(*, name: str = "World") -> None:
    """hello message"""
    from egoist.generators.clikit import runtime, clikit

    with runtime.generate(clikit) as m:
        hello = m.import_("m/hello")
        m.stmt(hello.Hello(name))


if __name__ == "__main__":
    app.run()
```

run command.

```console
# cmd/hello/main.go is generated
$ python definitions.py generate

$ go run cmd/hello/main.go
Hello World
$ go run cmd/hello/main.go -name Foo
Hello Foo
```

then, file structure is here.

```console
.
├── Makefile
├── cmd
│   └── hello
│       └── main.go
├── definitions.py
├── go.mod
└── hello
    └── hello.go

3 directories, 5 files
```

go.mod

```
module m

go 1.13
```

hello/hello.go

```go
package hello

import "fmt"

// Hello ...
func Hello(name string) {
	fmt.Println("Hello", name)
}
```

[cmd/hello/main.go](../examples/e2e/generate-clikit/03use-import/cmd/hello/main.go)

More details is [here](../examples/e2e/generate-clikit/03use-import).

## using DI in main.go

It partially supports DI like [google/wire](https://github.com/google/wire).

So, supporting following provider functions.

- `func() X`
- `func() (X, error)`
- `func() (X, func())`
- `func() (X, func(), error)`

definitions.py

```python
from egoist.app import App, SettingsDict

settings: SettingsDict = {"rootdir": "cmd/", "here": __file__}
app = App(settings)

app.include("egoist.directives.define_cli")


@app.define_cli("egoist.generators.clikit:walk")
def wire_example(*, grumby: bool = False) -> None:
    """
    google/wire event examples
    """
    from egoist.generators.clikit import runtime, clikit
    from egoist.go import di

    internal = app.maybe_dotted("internal")  # ./internal.py

    with runtime.generate(clikit) as m:
        b = di.Builder()

        # Greeter depends on Message
        # and, Event depends on Greeter
        b.add_provider(internal.NewMessage)
        b.add_provider(internal.NewGreeter)
        b.add_provider(internal.NewEvent)

        injector = b.build(variables=locals())
        event = injector.inject(m)
        m.stmt(event.Start())


if __name__ == "__main__":
    app.run()
```

run command.

```console
# cmd/wire_example/main.go is generated
$ python definitions.py generate


$ go run cmd/wire_example/main.go
Hi there!

$ go run cmd/wire_example/main.go -h
wire_example - google/wire event examples

Usage:
  -grumby
        -
exit status 1
$ go run cmd/wire_example/main.go -grumby
2020/04/30 20:21:27 !!could not create event: event greeter is grumpy
```

then, file structure is here.

```console
$ tree
.
├── Makefile
├── cmd
│   └── wire_example
│       └── main.go
├── definitions.py
├── go.mod
├── internal
│   └── components.go
└── internal.py

3 directories, 6 files
```

internal.py

```python
from __future__ import annotations
import typing as t
from egoist.go.types import GoError, gopackage


class Message:
    pass


class Greeter:
    pass


class Event:
    pass


@gopackage("m/internal")
def NewMessage() -> Message:
    pass


@gopackage("m/internal")
def NewGreeter(message: Message, grumby: bool) -> Greeter:
    pass


@gopackage("m/internal")
def NewEvent(g: Greeter) -> t.Tuple[Event, GoError]:
    pass
```

[internal/components.go](../examples/e2e/generate-clikit/04use-di/internal/components.go)
[cmd/wire_example/main.go](../examples/e2e/generate-clikit/04use-di/cmd/wire_example/main.go)

more details is [here](../examples/e2e/generate-clikit/04use-di).

## todo

- adding help message is [here](../examples/e2e/generate-clikit/01fullset)
- using cli rest args is [here](../examples/e2e/generate-clikit/05use-rest-args)

## todo

- [structkit](../examples/e2e/generate-structkit)

