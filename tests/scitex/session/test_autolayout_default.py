"""Regression test for scitex-python#214 — autolayout=False by default.

Before the fix, `@stx.session`-wrapped scripts silently inherited
`rcParams["figure.autolayout"] = True` and triggered
`UserWarning: This figure includes Axes that are not compatible with
tight_layout` on every savefig of a manually-positioned layout.

Fix: flip the default of `autolayout` from True to False in:
  - scitex.plt.utils._configure_mpl.configure_mpl
  - scitex.session._lifecycle._start.start
  - scitex.session._skills.lifecycle.md (docstring block)
"""

from __future__ import annotations

import inspect


class TestAutolayoutDefault:
    def test_configure_mpl_default_is_false(self):
        from scitex.plt.utils._configure_mpl import configure_mpl

        sig = inspect.signature(configure_mpl)
        assert sig.parameters["autolayout"].default is False

    def test_session_start_default_is_false(self):
        from scitex.session._lifecycle._start import start

        sig = inspect.signature(start)
        assert sig.parameters["autolayout"].default is False

    def test_skill_doc_lists_false(self):
        """The docstring / signature block in the session skill page
        must match the code default, or users get misled."""
        from pathlib import Path

        doc = (
            Path(
                inspect.getfile(__import__("scitex.session", fromlist=["_lifecycle"]))
            ).parent
            / "_skills"
            / "lifecycle.md"
        )
        if doc.exists():
            text = doc.read_text()
            # Only flag if the autolayout= kwarg is documented at all.
            if "autolayout=" in text:
                assert "autolayout=False" in text
                assert "autolayout=True" not in text


# EOF
