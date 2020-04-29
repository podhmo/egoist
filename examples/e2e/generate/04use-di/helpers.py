from __future__ import annotations
import typing as t
import typing_extensions as tx
from prestring.go.codeobject import Module, Symbol
from egoist.internal.graph import primitive, Graph
from egoist.internal.graph import topological_sorted
from egoist.internal._fnspec import fnspec, Fnspec


class Metadata(tx.TypedDict, total=False):
    return_type: t.Type[t.Any]
    component_type: t.Type[t.Any]
    fnspec: Fnspec


def parse(fn: t.Callable[..., t.Any]) -> t.Tuple[str, t.List[str], Metadata]:
    spec = fnspec(fn)

    depends = [
        primitive(name, metadata={"component_type": typ})
        if typ.__module__ == "builtins"
        else typ.__name__
        for name, typ, _ in spec.arguments
    ]

    return_type = spec.return_type
    if not hasattr(return_type, "__origin__"):
        component_type = return_type
    else:
        assert return_type.__origin__ == tuple, return_type.__origin__
        component_type, *_ = t.get_args(spec.return_type)

    metadata: Metadata = {
        "return_type": return_type,
        "component_type": component_type,
        "fnspec": spec,
    }
    return {
        "name": component_type.__name__,
        "depends": depends,
        "metadata": metadata,
    }


def new_variables(g: Graph, local_mapping: t.Dict[str, Symbol]) -> t.Dict[int, Symbol]:
    try:
        return {
            node.uid: local_mapping[node.name] for node in g.nodes if node.is_primitive
        }
    except KeyError as e:
        raise RuntimeError(f"arguments {e} is not found in {local_mapping.keys()}")


def inject(
    m: Module, g: Graph, *, variables: t.Dict[int, Symbol], strict: bool = True
) -> Symbol:
    # TODO: name
    i = 0
    for node in topological_sorted(g):
        if node.is_primitive:
            if strict:
                assert node.uid in variables
            else:
                variables[node.uid] = m.symbol(node.name)
            continue

        metadata = t.cast(Metadata, node.metadata)
        return_type = metadata.get("return_type", "")

        return_types = list(t.get_args(return_type) or [return_type])
        var_names = [
            f"v{i}",
            *[getattr(typ, "name", typ.__name__) for typ in return_types[1:]],
        ]

        spec: Fnspec = metadata.get("fnspec")
        provider_callable: t.Optional[Symbol] = None
        if spec is not None:
            pkg_prefix = m.import_(metadata["component_type"].gopackage)
            provider_callable = m.symbol(f"{pkg_prefix}.{spec.name}")
        if provider_callable is None:
            provider_callable = m.symbol(spec.name if spec else node.name)

        args = [variables[dep.uid] for dep in node.depends]
        variables[node.uid], *extra_vars = m.letN(var_names, provider_callable(*args))

        # xxx:
        if extra_vars:
            for sym, typ in sorted(
                zip(extra_vars, return_types[1:]),
                key=lambda pair: getattr(pair[1], "priority", 5),
                reverse=True,
            ):
                if hasattr(typ, "emit"):
                    typ.emit(m, sym)

        i += 1
    return variables[node.uid]
