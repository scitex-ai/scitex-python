"""SciTeX msword — thin compatibility shim for scitex-msword.

Aliases ``scitex.msword`` to the standalone ``scitex_msword`` package via
``sys.modules``. ``scitex.msword is scitex_msword``.

Public API: load_docx, save_docx, convert_docx_to_tex, list_profiles,
get_profile, register_profile, BaseWordProfile, WordReader, WordWriter,
link_captions_to_images, link_captions_to_images_by_proximity,
normalize_section_headings, validate_document, create_post_import_hook

Install: ``pip install scitex[msword]``  (or ``pip install scitex-msword``).
See: https://github.com/ywatanabe1989/scitex-msword
"""

import sys as _sys

try:
    import scitex_msword as _real
except ImportError as _e:  # pragma: no cover
    raise ImportError(
        "scitex.msword requires the 'scitex-msword' package. "
        "Install with: pip install scitex[msword]  (or: pip install scitex-msword)"
    ) from _e

_sys.modules[__name__] = _real
