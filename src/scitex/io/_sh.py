#!/usr/bin/env python3
"""Optional shell synergy for scitex.io.

`scitex-sh` is an optional extra (`scitex[sh]`). When installed, io's symlink
and cleanup helpers route through its richer `sh()` (logging, security checks);
when absent they fall back to a stdlib `subprocess` shim with identical
call semantics, so `scitex.io` works on a minimal install.
"""

from __future__ import annotations

from scitex_dev import try_import_optional

sh = try_import_optional("scitex_sh", "sh", extra="sh", pkg="scitex")

if sh is None:
    import subprocess

    def sh(command, verbose: bool = False):  # noqa: F811 — stdlib fallback
        """Minimal `scitex_sh.sh` shim: run an argv list, never raise."""
        if verbose:
            print(
                " ".join(map(str, command))
                if isinstance(command, (list, tuple))
                else command
            )
        return subprocess.run(command, check=False)


__all__ = ["sh"]
