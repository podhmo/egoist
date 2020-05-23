from egoist.app import create_app, SettingsDict, parse_args

settings: SettingsDict = {"rootdir": "", "here": __file__}
app = create_app(settings)

app.include("egoist.directives.define_cli")
app.include("egoist.directives.define_struct_set")


@app.define_struct_set("egoist.generators.structkit:walk")
def todo__models_gen() -> None:
    from egoist.generators.structkit import runtime, structkit
    import objects

    with runtime.generate(structkit, classes=[objects.Todo]) as m:
        m.package("todo")


@app.define_cli("egoist.generators.clikit:walk")
def cmd__todo() -> None:
    """todo message"""
    from egoist.generators.clikit import runtime, clikit

    with runtime.generate(clikit) as m:
        fmt_pkg = m.import_("fmt")
        time_pkg = m.import_("time")
        todo_pkg = m.import_("m/todo")

        err = m.symbol("err")
        x = m.symbol("x")
        args = runtime.get_cli_rest_args()

        # s := new(todo.TodoStore)
        s = m.let("s", m.symbol("new")(todo_pkg.TodoStore))
        # s.Filename = "todo.json"
        m.stmt(f'{s}.Filename = "todo.json"')
        # s.Now = time.Now
        m.stmt(f'{s}.Now = {time_pkg}.Now')
        m.sep()

        # if err := s.Load(); err != nil {
        # 	return err
        # }
        with m.if_(f"{err} := {s.Load()}; {err} != nil"):
            m.return_(err)

        # for _, x := range opt.Args {
        # 	todo.Add(x)
        # }
        with m.for_(f"_, {x} := range {args}"):
            m.stmt(s.Add(x))

        # for _, x := range todo.List() {
        # 	fmt.Println(x)
        # }
        with m.for_(f"_, {x} := range {s.List()}"):
            m.stmt(fmt_pkg.Println(x))

        # if err := todo.Save(); err != nil {
        # 	return err
        # }
        with m.if_(f"{err} := {s.Save()}; {err} != nil"):
            m.return_(err)


if __name__ == "__main__":
    for argv in parse_args(sep="-"):
        app.run(argv)
