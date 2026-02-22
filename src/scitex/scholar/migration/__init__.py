#!/usr/bin/env python3
"""Connected Papers migration for scitex.scholar.

Import: Fetch a Connected Papers graph and convert to CitationGraph or Papers.
Export: Convert CitationGraph to BibTeX/JSON importable by CP web UI.

Usage::

    from scitex.scholar.migration import from_connected_papers, to_connected_papers

    result = from_connected_papers("649def34f8be52c8b66281af98ae884c09aef38b")
    result = to_connected_papers(graph, output="./export")
"""

from __future__ import annotations

from ._connected_papers import from_connected_papers, to_connected_papers

__all__ = ["from_connected_papers", "to_connected_papers"]

# Hide leaked submodule attributes
import sys as _sys

_this = _sys.modules[__name__]
for _name in ["_connected_papers", "_s2_resolver"]:
    try:
        delattr(_this, _name)
    except AttributeError:
        pass
del _this, _name, _sys

# EOF
