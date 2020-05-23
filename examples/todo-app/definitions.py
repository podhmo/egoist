from egoist.app import create_app, SettingsDict, parse_args

settings: SettingsDict = {"rootdir": "", "here": __file__}
app = create_app(settings)

app.include("egoist.directives.define_cli")
app.include("egoist.directives.define_struct_set")


@app.define_struct_set("egoist.generators.structkit:walk")
def todo__models() -> None:
    from egoist.go.types import gopackage
    from egoist.generators.structkit import runtime, structkit

    @gopackage("time")
    class Time:
        pass

    class Todo:
        Content: str
        CreatedAt: Time

    with runtime.generate(structkit, classes=[Todo]) as m:
        m.package("todo")


@app.define_cli("egoist.generators.clikit:walk")
def cmd__todo() -> None:
    """todo message"""
    from egoist.generators.clikit import runtime, clikit

    with runtime.generate(clikit) as m:
        todo_pkg = m.import_("m/todo")
        fmt_pkg = m.import_("fmt")

        err = m.symbol("err")
        x = m.symbol("x")
        args = runtime.get_cli_rest_args()

        # if err := todo.Load(); err != nil {
        # 	return err
        # }
        with m.if_(f"{err} := {todo_pkg.Load()}; {err} != nil"):
            m.return_(err)

        # for _, x := range opt.Args {
        # 	todo.Add(x)
        # }
        with m.for_(f"_, {x} := range {args}"):
            m.stmt(todo_pkg.Add(x))

        # for _, x := range todo.List() {
        # 	fmt.Println(x)
        # }
        with m.for_(f"_, {x} := range {todo_pkg.List()}"):
            m.stmt(fmt_pkg.Println(x))

        # if err := todo.Save(); err != nil {
        # 	return err
        # }
        with m.if_(f"{err} := {todo_pkg.Save()}; {err} != nil"):
            m.return_(err)


if __name__ == "__main__":
    for argv in parse_args(sep="-"):
        app.run(argv)
