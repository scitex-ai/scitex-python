"""scitex._integration — cross-peer glue code that lives in the umbrella.

Most umbrella imports of the form ``scitex.<short>`` resolve via the
alias finder (see ``scitex._aggregator``) to the corresponding peer
standalone (``scitex_<short>``). The umbrella ships no duplicate impl;
peers are the single source of truth.

This package exists for the residual case: code that legitimately
depends on **two or more** peers and would create a circular dep if
placed in any single one. Examples:

- A workflow that runs ``scitex_clew`` then ``scitex_writer``.
- A bundle format combining ``scitex_io`` + ``scitex_plt`` +
  ``scitex_stats`` outputs.
- A cross-peer health check that probes every peer.

Anything that's a wrapper around a single peer is NOT integration —
it belongs in that peer's repo.
"""

from __future__ import annotations

__all__: list[str] = []
