"""Plan public peer tool names without copying callbacks or changing a leaf."""

from dataclasses import dataclass

from ._compat import get_tools_sync

# Historical ownership names accepted at the umbrella boundary only.
_LEGACY_PREFIXES = {"hub": ("cloud",), "sdk": ("app",)}


@dataclass(frozen=True)
class MountPlan:
    server: object
    tool_names: dict[str, str]
    local_names: frozenset[str]


def prepare_mount(server, namespace: str) -> MountPlan:
    """Remove redundant leading owner prefixes, rejecting ambiguous names.

    FastMCP applies these renames before its normal namespace transform.
    Resources, prompts, middleware and leaf callback routing stay mounted.
    Run discovery inside the same bounded worker as peer resolution.
    """
    prefixes = (namespace, *_LEGACY_PREFIXES.get(namespace, ()))
    names = {}
    owners = {}
    for original in get_tools_sync(server):
        local = original
        while True:
            prefix = next(
                (p + "_" for p in prefixes if local.startswith(p + "_")), None
            )
            if prefix is None:
                break
            local = local[len(prefix) :]
        if not local:
            raise ValueError(f"Empty tool name after namespacing: {original!r}")
        if local in owners:
            raise ValueError(
                f"Tool name collision for {namespace}_{local}: "
                f"{owners[local]!r} and {original!r}"
            )
        owners[local] = original
        if local != original:
            names[original] = local
    return MountPlan(server, names, frozenset(owners))
