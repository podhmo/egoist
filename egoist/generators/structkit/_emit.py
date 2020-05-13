from __future__ import annotations
import typing as t
import typing_inspect as ti
import inspect
from prestring.go import goname
from prestring.naming import untitleize
import metashape.typeinfo as typeinfo
from egoist.go.types import _unwrap_pointer_type
from ._context import Context, Item
from . import runtime


def build_tag_string(tags: t.Dict[str, t.List[str]]) -> str:
    return " ".join(f'''{k}:"{', '.join(vs)}"''' for k, vs in tags.items())


def has_reference(info: typeinfo.TypeInfo) -> bool:
    return info.user_defined_type is not None


def emit_struct(ctx: Context, item: Item) -> runtime.Definition:
    m = ctx.m
    resolver = ctx.resolver

    typename = str(resolver.resolve_gotype(item.type_))

    # // <typename> ...
    doc = inspect.getdoc(item.type_)
    if doc:
        lines = doc.split("\n")
        m.stmt(f"// {typename} {lines[0]}")
        for line in lines[1:]:
            m.stmt(f"// {line}")

    # type <typename> struct {
    # ...
    # }
    m.stmt(f"type {typename} struct {{")
    with m.scope():
        for name, info, metadata in item.fields:
            raw_type = ctx.raw_type_map.get(info) or info.raw

            if raw_type in ctx.pseudo_item_map:
                gotype: str = ctx.pseudo_item_map[raw_type].name
            else:
                gotype = resolver.resolve_gotype(raw_type)

            # handling field (private field?, embedded?)
            if metadata.get("inline", False):
                m.append(gotype)
            elif name.startswith("_"):
                m.append(f"{untitleize(goname(name))} {gotype}")
            else:
                m.append(f"{goname(name)} {gotype}")

            # note: metadata['tags'] is injected by _walker.walk()
            m.append(f" `{build_tag_string(metadata['tags'])}`")

            # handling comments
            if metadata.get("inline", False):
                m.stmt(f"  // {metadata}")
            else:
                comment = metadata.get("comment", "")
                m.stmt(f"  // {comment.split(_NEWLINE, 1)[0]}" if comment else "")

    m.stmt("}")
    return runtime.Definition(name=typename, code_module=None)


def emit_union(ctx: Context, item: Item) -> runtime.Definition:
    m = ctx.m
    resolver = ctx.resolver

    typename = goname(item.name)
    kind_typename = typename + "Kind"

    # type <typename> {
    #     Kind string `json:"$kind"`
    # ...
    # }
    m.stmt(f"type {typename} struct {{")
    with m.scope():
        m.stmt(f'Kind {kind_typename} `json:"$kind"` // discriminator')
        for subtype in item.args:
            gotype: str = resolver.resolve_gotype(subtype)
            m.append(f"{gotype} *{gotype}")
            m.stmt(f' `json:"{untitleize(str(gotype)).rstrip("_")},omitempty"`')

    m.stmt("}")
    m.sep()

    # UnmarshalJSON
    pseudo_item = ctx.create_pseudo_item(item, discriminator_name=kind_typename)
    unmarshalJSON_definition = emit_unmarshalJSON(ctx, pseudo_item)
    m.sep()

    # one-of validation
    assert unmarshalJSON_definition.code_module is not None
    this = m.symbol(f"{item.name[0].lower()}")
    maperr_pkg = m.import_("github.com/podhmo/maperr")

    sm = unmarshalJSON_definition.code_module
    sm.stmt("// one-of?")
    sm.stmt("{")
    with sm.scope():
        for go_name, info, _ in pseudo_item.fields[1:]:
            with sm.if_(f'{this}.Kind == "{go_name}" && {this}.{go_name} == nil'):
                sm.stmt(
                    f'err = err.Add("{go_name}", {maperr_pkg}.Message{{Text: "treated as {go_name}, but no data"}})'
                )
    sm.stmt("}")

    # enums
    emit_enums(ctx, item.type_, name=kind_typename)

    return runtime.Definition(name=typename, code_module=None)


def emit_enums(
    ctx: Context, literal_type: t.Type[t.Any], *, name: t.Optional[str] = None,
) -> runtime.Definition:
    m = ctx.m
    resolver = ctx.resolver

    # literal_type or union_type
    go_type = name or f"{resolver.resolve_gotype(literal_type)}"

    first_of_args = ti.get_args(literal_type)[0]
    base_go_type = resolver.resolve_gotype(
        type(getattr(first_of_args, "__name__", first_of_args))
    )

    const_names = [getattr(x, "__name__", x) for x in ti.get_args(literal_type)]
    const_members = {name: f"{go_type}{goname(name)}" for name in const_names}
    this = m.symbol("v")
    as_literal = resolver.resolve_default

    # type <enum> string
    m.stmt(f"type {go_type} {base_go_type}")
    m.sep()

    # const (
    #     <enum>xxx <enum> = "xxx"
    # ...
    # )
    with m.const_group() as cg:
        for name in const_names:
            cg(f"{const_members[name]} {go_type} = {as_literal(type(name), name)}")
    m.sep()

    # func (v <enum>) Valid() error {
    # ...
    # }
    with m.method(f"{this} {go_type}", "Valid", returns="error"):
        with m.switch(str(this)) as sm:
            with sm.case(", ".join(const_members.values())):
                sm.return_("nil")
            with sm.default():
                fmt_pkg = m.import_("fmt")
                candidates = ", ".join([str(x) for x in const_names])
                sm.return_(
                    fmt_pkg.Errorf(
                        as_literal(str, f"%q is invalid enum value of ({candidates})"),
                        this,
                    )
                )
        sm.unnewline()

    # func (v <enum>) UnmarshalJSON(b []byte) error {
    # ...
    # }
    with m.method(f"{this} *{go_type}", "UnmarshalJSON", "b []byte", returns="error"):
        strings_pkg = m.import_("strings")
        m.stmt(f'*{this} = {go_type}({strings_pkg}.Trim(string(b), `"`))')
        m.return_(this.Valid())

    return runtime.Definition(name=go_type, code_module=None)


def emit_unmarshalJSON(ctx: Context, item: Item) -> runtime.Definition:
    m = ctx.m
    resolver = ctx.resolver

    this = m.symbol(f"{item.name[0].lower()}")
    this_type = f"{resolver.resolve_gotype(item.type_)}"
    this_type_pointer = f"*{this_type}"

    # func (ob *Ob) UnmarshalJSON(b []byte) error {
    b = m.symbol("b")
    m.stmt(f"func ({this} {this_type_pointer}) UnmarshalJSON({b} []byte) error {{")
    with m.scope():

        # var err *maperr.Error
        err = m.symbol("err")
        maperr_pkg = m.import_("github.com/podhmo/maperr")
        m.stmt(f"var {err} *{maperr_pkg}.Error")
        m.sep()

        # var inner struct {
        #   ...
        # }
        m.stmt("// loading internal data")
        inner = m.symbol("inner")
        m.stmt(f"var {inner} struct {{")
        with m.scope():
            for name, info, metadata in item.fields:
                if name.startswith("_"):
                    continue  # xxx:

                raw_type = ctx.raw_type_map.get(info) or info.raw
                if has_reference(info):
                    json_pkg = m.import_("encoding/json")
                    gotype = str(json_pkg.RawMessage)
                else:
                    gotype = resolver.resolve_gotype(raw_type)

                m.append(f'{goname(name)} *{gotype} `json:"{name}"`')
                m.stmt("// required" if metadata["required"] else "")
        m.stmt("}")

        # if rawErr := json.Unmarshal(b, &inner); rawErr != nil {
        # ...
        # }
        json_pkg = m.import_("encoding/json")
        raw_err = m.symbol("rawErr")
        with m.if_(f"{raw_err} := {json_pkg}.Unmarshal(b, &{inner}); {raw_err} != nil"):
            m.return_(err.AddSummary(raw_err.Error()))
        m.sep()

        # if <field> != nil {
        #     ob.<field> = *<field>
        # } else {
        #     m.add(<field>, "required")
        # }
        rawerr = m.symbol("rawerr")
        m.stmt("// binding field value and required check")
        with m.block():
            for name, info, metadata in item.fields:
                field = m.symbol(goname(name))
                with m.if_(f"{inner}.{field} != nil"):
                    if has_reference(info):
                        if info.is_optional or info in ctx.raw_type_map:  # pointer
                            raw_type = ctx.raw_type_map.get(info) or info.raw
                            level = max(1, _unwrap_pointer_type(raw_type)[1])
                            gotype = resolver.resolve_gotype(info.type_)

                            # NOTE: tricky code
                            #
                            # when *X   (1 level), generated code:
                            #     ob.<attr> = &X{}
                            # when **X  (2 level), generated code:
                            #     v0 := &X{}
                            #     ob.<attr> = &v0
                            # when ***X (3 level), generated code:
                            #     v0 := &X{}
                            #     v1 := &v0
                            #     ob.<attr> = &v1
                            syms = [(":=", f"{gotype}{{}}")]
                            for i in range(level - 1):
                                syms.append((":=", f"v{i}"))
                            syms.append(("=", f"{this}.{goname(name)}"))
                            for i in range(1, len(syms)):
                                _, rhs = syms[i - 1]
                                op, lhs = syms[i]
                                m.stmt(f"{lhs} {op} &{rhs}")

                            ref = f"{this}.{field}"
                        elif (
                            info.is_container
                            and info.args
                            and info.container_type != "union"
                        ):
                            gotype = resolver.resolve_gotype(info.type_)
                            m.stmt(f"{this}.{goname(name)} = {gotype}{{}}")
                            ref = f"&{this}.{field}"
                        else:
                            ref = f"&{this}.{field}"

                        with m.if_(
                            f"{rawerr} := json.Unmarshal(*{inner}.{field}, {ref}); {rawerr} != nil"
                        ):
                            m.stmt(
                                f'{err} = {err}.Add("{name}", {maperr_pkg}.Message{{Error: {rawerr}}})'
                            )
                    else:
                        m.stmt(f"{this}.{field} = *{inner}.{field}")
                if metadata["required"]:
                    with m.else_():
                        m.stmt(
                            f'{err} = err.Add("{name}", {maperr_pkg}.Message{{Text: "required"}})'
                        )
        m.sep()

        # NOTE: for injecting code from extrnal area
        code_module = m.submodule("", newline=False)

        # return err.Untyped()
        m.return_(err.Untyped())

    m.stmt("}")
    return runtime.Definition(name="UnmarshalJSON", code_module=code_module)


_NEWLINE = "\n"
