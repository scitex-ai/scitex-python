#!/usr/bin/env python3
"""Tests for ``scitex._canonical_redirects``.

The redirect map converts a "scitex.gen.X requires scitex[gen]" install
trap (when X actually lives in scitex.io / scitex.session / ...) into a
sharper hint that names the canonical location. This module pins:

* The seed redirect entries from proj-paper-ripple-wm's PR#4a audit are
  present (sanity check the map is wired up).
* ``venv_pip_hint`` returns ``{sys.executable} -m pip install
  'scitex[<name>]'`` so venv users don't accidentally pip-install into
  the system Python.
* ``missing_extras_hint`` names the canonical location when a redirect
  exists, falls back to the venv-pip hint otherwise.
* ``phantom_attr_hint`` returns ``None`` when no redirect exists (let the
  original AttributeError propagate) and a sharp message when one does.
"""

import sys

import pytest

from scitex._canonical_redirects import (
    CANONICAL_REDIRECTS,
    missing_extras_hint,
    phantom_attr_hint,
    venv_pip_hint,
)


class TestSeedRedirects:
    """The PR#4a audit's confirmed misdirections all have a canonical home
    in a core-deps peer. These rows must survive any future map edit."""

    @pytest.mark.parametrize(
        ("short", "attr", "expected"),
        [
            # gen → io
            ("gen", "load_configs", "io"),
            ("gen", "glob", "io"),
            ("gen", "reload", "io"),
            # gen → session
            ("gen", "start", "session"),
            ("gen", "close", "session"),
            # gen → dict
            ("gen", "replace", "dict"),
            ("gen", "listed_dict", "dict"),
            # gen → str
            ("gen", "search", "str"),
            # gen → etc
            ("gen", "yield_grids", "etc"),
            ("gen", "count_grids", "etc"),
            # gen → context
            ("gen", "suppress_output", "context"),
            # gen → types
            ("gen", "is_listed_X", "types"),
        ],
    )
    def test_seed_entry_present(self, short, attr, expected):
        # Arrange
        key = (short, attr)
        # Act
        home = CANONICAL_REDIRECTS.get(key)
        # Assert
        assert home == expected


class TestVenvPipHint:
    """``venv_pip_hint`` uses ``{sys.executable} -m pip install
    'scitex[<extras>]'`` (B.3) so venv users don't accidentally install
    into a system-level Python; quotes the spec so shells that glob
    square brackets don't choke."""

    def test_uses_sys_executable(self):
        # Arrange
        short = "gen"
        # Act
        hint = venv_pip_hint(short)
        # Assert
        assert sys.executable in hint

    def test_uses_module_invocation(self):
        # Arrange
        short = "gen"
        # Act
        hint = venv_pip_hint(short)
        # Assert
        assert "-m pip install" in hint

    def test_quotes_extras_spec(self):
        # Arrange
        short = "gen"
        # Act
        hint = venv_pip_hint(short)
        # Assert — the literal `'scitex[gen]'` quoted form, not the bare
        # `scitex[gen]` form, so zsh's filename-globbing doesn't barf.
        assert "'scitex[gen]'" in hint


class TestMissingExtrasHint:
    """``missing_extras_hint`` is used when the lazy module's underlying
    package is not importable — the extras-gate case. With a known
    canonical redirect it names the right module; without one it falls
    back to the venv-pip hint."""

    def test_known_redirect_names_canonical_module(self):
        # Arrange
        short, attr = "gen", "load_configs"
        # Act
        hint = missing_extras_hint(short, attr)
        # Assert
        assert "scitex.io.load_configs" in hint

    def test_known_redirect_announces_no_extra_needed(self):
        # Arrange
        short, attr = "gen", "load_configs"
        # Act
        hint = missing_extras_hint(short, attr)
        # Assert — the message must reassure the user they DON'T need to
        # pip-install heavy extras for a callsite they can just rewrite.
        assert "no extra needed" in hint

    def test_known_redirect_suggests_from_import_rewrite(self):
        # Arrange
        short, attr = "gen", "load_configs"
        # Act
        hint = missing_extras_hint(short, attr)
        # Assert
        assert "from scitex.io import load_configs" in hint

    def test_unknown_redirect_hint_names_venv_executable(self):
        # Arrange
        short, attr = "audio", "some_attr_with_no_redirect"
        # Act
        hint = missing_extras_hint(short, attr)
        # Assert — without a redirect the generic missing-extras hint is
        # still venv-correct (names the current interpreter).
        assert sys.executable in hint

    def test_unknown_redirect_hint_names_the_extra_spec(self):
        # Arrange
        short, attr = "audio", "some_attr_with_no_redirect"
        # Act
        hint = missing_extras_hint(short, attr)
        # Assert
        assert "'scitex[audio]'" in hint


class TestPhantomAttrHint:
    """``phantom_attr_hint`` is used when the lazy module's package IS
    loaded but the attribute does not exist on it. Returns ``None`` when
    there's no redirect (caller lets the original AttributeError
    propagate) and a sharp message when there is."""

    def test_returns_none_when_no_redirect(self):
        # Arrange
        short, attr = "audio", "definitely_not_in_redirect_map"
        # Act
        hint = phantom_attr_hint(short, attr)
        # Assert
        assert hint is None

    def test_known_redirect_returns_string_naming_canonical(self):
        # Arrange
        short, attr = "gen", "load_configs"
        # Act
        hint = phantom_attr_hint(short, attr)
        # Assert
        assert hint is not None and "scitex.io.load_configs" in hint

    def test_known_redirect_uses_attribute_error_phrasing(self):
        # Arrange
        short, attr = "gen", "load_configs"
        # Act
        hint = phantom_attr_hint(short, attr)
        # Assert — message should say "module ... has no attribute X" so
        # it reads naturally when raised as AttributeError(message).
        assert "has no attribute" in hint


# EOF
