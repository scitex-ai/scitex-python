"""Re-export shim — caption system moved to figrecipe._captions.

Phase 4 of the figrecipe-owns-plt rebalance (2026-05-08). The
canonical caption system lives in ``figrecipe._captions`` (which
already had a parallel implementation predating this migration).
This module:

  - Re-exports the 7 generic caption symbols from figrecipe so existing
    ``from scitex.plt.utils._scientific_captions import …`` callers
    keep working.
  - Keeps the 2 scitex-integration helpers (``save_with_caption``,
    ``enhance_scitex_save_with_captions``) here, because they wrap
    ``scitex.io.save`` — figrecipe is a leaf dependency and must not
    import scitex.
"""

# Re-export the canonical caption surface from figrecipe.
from figrecipe._captions import (  # noqa: F401
    ScientificCaption,
    add_figure_caption,
    add_panel_captions,
    caption_manager,
    create_figure_list,
    cross_ref,
    export_captions,
    quick_caption,
)
# scitex.plt.utils.__init__ imports format helpers under the
# underscore-prefixed names; figrecipe exposes them publicly.
# Alias for back-compat:
from figrecipe._captions import escape_latex as _escape_latex  # noqa: F401
from figrecipe._captions import format_caption_for_md as _format_caption_for_md  # noqa: F401
from figrecipe._captions import format_caption_for_tex as _format_caption_for_tex  # noqa: F401
from figrecipe._captions import format_caption_for_txt as _format_caption_for_txt  # noqa: F401
from figrecipe._captions import save_caption_multiple_formats as _save_caption_multiple_formats  # noqa: F401

__all__ = [
    "ScientificCaption",
    "add_figure_caption",
    "add_panel_captions",
    "create_figure_list",
    "cross_ref",
    "export_captions",
    "quick_caption",
    "save_with_caption",
    "enhance_scitex_save_with_captions",
]


# ---------------------------------------------------------------------------
# scitex-integration helpers — kept here because they wrap scitex.io.save.
# ---------------------------------------------------------------------------
def save_with_caption(fig, filename: str, caption: str = None, **caption_kwargs):
    """Save a figure via scitex.io.save and optionally write caption files.

    Caption files are written via figrecipe's
    ``save_caption_multiple_formats`` (TXT / TeX / MD) using the same
    base filename. Equivalent to calling ``scitex.io.save(fig, filename)``
    plus the figrecipe caption helper, but in one step.
    """
    import scitex

    scitex.io.save(fig, filename)

    if caption:
        base_name = filename.split(".")[0]
        _save_caption_multiple_formats(caption, base_name, **caption_kwargs)
        formatted_caption = add_figure_caption(fig, caption, **caption_kwargs)
        return formatted_caption
    return None


def enhance_scitex_save_with_captions():
    """Monkey-patch ``scitex.io.save`` to honour a ``caption=`` kwarg.

    After calling this, every ``scitex.io.save(fig, filename, caption=…)``
    will additionally write the caption in multiple formats next to the
    saved figure.
    """
    import scitex

    original_save = scitex.io.save

    def enhanced_save(obj, filename, caption=None, **kwargs):
        result = original_save(obj, filename, **kwargs)
        if caption is not None and hasattr(obj, "savefig"):
            base_name = filename.split(".")[0]
            _save_caption_multiple_formats(caption, base_name)
        return result

    scitex.io.save = enhanced_save
    return enhanced_save
