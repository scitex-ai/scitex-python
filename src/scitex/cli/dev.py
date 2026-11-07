"""Umbrella development namespace, delegated to owning command groups."""

import re
from pathlib import Path

import click

from ._lazy_subcommands import build_lazy_subcommands, reserved_cli_names
from .main import LazyGroup
from .main import cli as root_cli

_LOCAL = {
    name: (f"scitex.cli.{name}", name, help_text)
    for name, help_text in {
        "audit": "Security auditing tools.",
        "completion": "Manage completion for the scitex command.",
        "introspect": "Inspect Python APIs and documentation.",
        "pkg": "Inspect installed package drift.",
    }.items()
}
_LOCAL["list-python-apis"] = (
    "scitex.cli._list_python_apis",
    "list_python_apis",
    "List SciTeX Python APIs.",
)


class DevGroup(LazyGroup):
    """View of Dev's real groups with umbrella-owned workflows added lazily.

    The shared owner object is never mutated. In particular skills resolves
    to Dev's canonical group, rather than the old second umbrella inventory.
    """

    def __init__(self, snapshot=None):
        from scitex_dev._cli import main as owner
        from scitex_dev.ecosystem import deprecated_alias

        snapshot = root_cli._exposure_snapshot if snapshot is None else snapshot
        self._exposure_snapshot = snapshot
        self._owner = owner
        self._upkeep = owner.get_command(None, "dev")
        self._blocked = reserved_cli_names(snapshot=snapshot, namespace="dev")
        local = {
            name: spec for name, spec in _LOCAL.items() if name not in self._blocked
        }
        local.update(
            build_lazy_subcommands(
                str(Path(__file__).parent), namespace="dev", snapshot=snapshot
            )
        )
        super().__init__(
            name="dev",
            callback=owner.callback,
            params=list(owner.params),
            context_settings=dict(owner.context_settings),
            invoke_without_command=True,
            add_help_option=False,
            lazy_subcommands=local,
            exposure_snapshot=snapshot,
            help="Developer tools, audits, package checks, skills, and completion.",
        )
        deprecated_alias(
            self,
            "dev",
            target=self,
            target_name="dev",
            remove_in="3.0",
        )

    def with_exposure(self, snapshot):
        """Bind a fresh Root construction without mutating the shared Dev owner."""
        return self if snapshot is self._exposure_snapshot else type(self)(snapshot)

    def list_commands(self, ctx):
        """List the shared domain and flattened maintenance workflows."""
        names = set(super().list_commands(ctx)) | set(self._owner.list_commands(ctx))
        if isinstance(self._upkeep, click.Group):
            names.update(self._upkeep.list_commands(ctx))
        visible = []
        for name in sorted(names - self._blocked):
            # Local lazy entries have already passed metadata eligibility.
            # Do not import them merely to list the composed namespace.
            if name in self._lazy_subcommands:
                visible.append(name)
                continue
            command = self.get_command(ctx, name)
            if command is not None and not command.hidden:
                visible.append(name)
        return visible

    def get_command(self, ctx, name):
        """Resolve an owned command without changing its shared group."""
        if name in self._blocked:
            return None
        if name == "dev":
            # Legacy double-dev must re-enter this effective view, not the
            # raw owner group, or it could resurrect a declined command.
            return self.commands.get("dev")
        if name in self.commands:
            return self.commands[name]
        if name in self._lazy_subcommands:
            return self._load_lazy(name)
        if name != "dev" and isinstance(self._upkeep, click.Group):
            command = self._upkeep.get_command(ctx, name)
            if command is not None:
                return self._project_alias(name, command)
        return self._project_alias(name, self._owner.get_command(ctx, name))

    def _project_alias(self, name, command):
        """Resolve owner-authored canonical alias metadata through this view."""
        from scitex_dev.ecosystem import deprecated_alias

        metadata = getattr(command, "_deprecated_alias", None)
        if metadata is None:
            # An inherited hidden closure without a canonical declaration
            # cannot be projected safely through a different policy scope.
            return command if command is not None and not command.hidden else None
        if not isinstance(metadata, dict):
            return None
        # The shared helper records canonical target paths for static audits.
        # Reuse that declaration rather than invoke an alias closure captured
        # against the unfiltered owner group. Unstructured aliases fail closed.
        target = metadata.get("target")
        if not isinstance(target, str):
            return None
        path = tuple(target.split())
        if (
            not path
            or path[0] == name
            or path[0] in self._blocked
            or any(not re.fullmatch(r"[a-z][a-z0-9-]*", part) for part in path)
            or metadata.get("phase") not in {"warn", "error"}
            or not isinstance(metadata.get("remove_in"), str)
        ):
            return None
        return deprecated_alias(
            self,
            name,
            target=path,
            remove_in=metadata["remove_in"],
            phase=metadata["phase"],
        )

    def command_summaries(self, ctx):
        """Return visible descriptions for the composed Dev view."""
        rows = []
        for name in self.list_commands(ctx):
            if name in self._lazy_subcommands:
                rows.append((name, self._lazy_subcommands[name][2]))
                continue
            command = self.get_command(ctx, name)
            if command is not None and not command.hidden:
                rows.append((name, command.get_short_help_str(limit=150)))
        return rows


dev = DevGroup()
