#!/usr/bin/env python3
"""Thin shim re-exporting scitex_notebook (standalone package).

All implementation lives in the ``scitex-notebook`` package. This module
exists for backward compatibility of ``scitex.notebook.*`` imports.
"""

from scitex_notebook import (  # noqa: F401
    CompiledNotebook,
    __all__,  # noqa: F401
    __version__,
    check_notebook,
    compile_notebook,
    convert_notebook,
    get_code_cells,
    get_notebook_name,
    parse_notebook,
    verify_notebook,
)

# EOF
