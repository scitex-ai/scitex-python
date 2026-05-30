#!/usr/bin/env python3
"""Scitex utils — thin re-export aggregator.

This is a grab-bag namespace with no single owning package. Each public
helper now lives in its SoC-correct standalone and is re-exported here for
backward compatibility (``stx.utils.<name>`` keeps working):

- ``compress_hdf5``           → scitex-io
- ``count_grids`` / ``yield_grids`` / ``search`` → scitex-etc
- ``notify`` (+ ``_send_gmail`` / ``_gen_footer`` / host helpers) → scitex-notification

New code should import from the owning package directly. The in-tree
implementations were removed (the migration moved them to the standalones);
``_verify_scitex_format`` remains here pending its move to scitex-dev.
"""

from scitex_etc import count_grids, search, yield_grids
from scitex_io import compress_hdf5
from scitex_notification import notify

# Backward-compat private aliases (were exposed as private names by the old
# in-tree utils; unused outside this module, kept to avoid any surprise).
from scitex_notification._notify_legacy import ansi_escape as _ansi_escape
from scitex_notification._notify_legacy import gen_footer as _gen_footer
from scitex_notification._notify_legacy import get_git_branch as _get_git_branch
from scitex_notification._notify_legacy import get_hostname as _get_hostname
from scitex_notification._notify_legacy import get_username as _get_username
from scitex_notification._notify_legacy import send_gmail as _send_gmail

__all__ = [
    # Public API (re-exported from owning standalones)
    "compress_hdf5",
    "count_grids",
    "yield_grids",
    "notify",
    "search",
]
