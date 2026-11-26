#!/usr/bin/env python3
"""Hidden aliases for umbrella commands renamed to the CLI convention.

The 2026-11-19 CLI standardization renamed umbrella commands to the
noun/verb grammar that ``scitex-dev ecosystem audit-cli`` enforces. The
old names keep working: each is a hidden Phase-W alias built by
scitex-dev's shared ``deprecated_alias`` helper (doctrine
``11_deprecation.md``). An alias forwards every argument and option to
the new command and prints a one-line note to stderr::

    'history' is deprecated — use 'list' (removed in v3.0)

The note is printed once per shell session (scitex-dev keys it on the
parent shell's PID). Hidden aliases are not listed in ``--help``.
"""

from __future__ import annotations

import click

#: Version in which every alias registered here is removed.
REMOVE_IN = "3.0"


def alias_renamed(group: click.Group, renames: dict[str, str]) -> None:
    """Register ``{old: new}`` leaf renames on ``group`` as hidden aliases.

    ``new`` must already be a command on ``group``; a missing target is a
    wiring bug and raises immediately instead of failing at dispatch.
    """
    from scitex_dev.ecosystem import deprecated_alias

    for old, new in renames.items():
        target = group.commands.get(new)
        if target is None:
            raise KeyError(f"alias {old!r}: {new!r} is not a command of {group.name!r}")
        deprecated_alias(group, old, target=target, remove_in=REMOVE_IN)


# EOF
