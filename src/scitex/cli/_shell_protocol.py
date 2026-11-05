"""Shared shell bootstrap without importing the developer CLI during discovery."""

import click


class _ShellProtocolCommand(click.Command):
    """Resolve the real shared command only when this protocol is selected."""

    def __init__(self, name):
        super().__init__(name, hidden=True)
        self._delegate = None

    def _load(self):
        if self._delegate is None:
            from scitex_dev._cli._completion import attach_shell_completion

            # Its legacy `completion` alias stays in this temporary registry;
            # it must not replace Root's actual developer completion group.
            holder = click.Group()
            attach_shell_completion(holder, prog_name="scitex")
            self._delegate = holder.commands[self.name]
        return self._delegate

    def get_params(self, ctx):
        return self._load().get_params(ctx)

    def get_help(self, ctx):
        return self._load().get_help(ctx)

    def invoke(self, ctx):
        return self._load().invoke(ctx)


def _register_shell_protocol(cli, *, blocked):
    """Mount admitted callbacks without adding normal-listing or import noise."""
    lazy = getattr(cli, "_lazy_subcommands", {})
    if "dev" not in lazy or "completion" in blocked:
        return
    for name in ("install-shell-completion", "print-shell-completion"):
        if name in blocked or name in lazy or name in cli.commands:
            continue
        cli.add_command(_ShellProtocolCommand(name), name)
