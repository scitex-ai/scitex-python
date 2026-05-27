#!/usr/bin/env python3
# Timestamp: 2026-05-16
# File: tests/scitex/test_subset_identity_peers.py
"""Subset-identity tests for every scitex_<x> ↔ scitex.<x> peer pair.

For every standalone scitex_<x> peer, every public name reachable on the
peer must also be reachable on the umbrella scitex.<x>. The umbrella is
allowed to add umbrella-only extras on top (Bundle integration, etc.) —
this is asymmetric: peer ⊆ umbrella.

Designed during the branding-translation initiative on 2026-05-16. See
~/proj/scitex-lead/GITIGNORED/BRANDING_TRANSLATION.md for the broader
plan (this is the Phase 3 forcing-function test).

The `annotations` symbol is uniformly ignored — it's the `from __future__
import annotations` binding present on the standalones but not on the
umbrella wrappers. Pure noise.
"""

from __future__ import annotations

import importlib

import pytest

# (standalone_module, umbrella_attr) pairs.
# Order chosen to put the simple/clean ones first so failures on the
# entangled ones (plt) are easy to spot at the bottom of pytest output.
PEERS: list = [  # list[tuple[str, str] | pytest.ParameterSet]
    ("scitex_io", "scitex.io"),
    ("scitex_stats", "scitex.stats"),
    ("scitex_dsp", "scitex.dsp"),
    ("scitex_config", "scitex.config"),
    ("scitex_gen", "scitex.gen"),
    ("scitex_pd", "scitex.pd"),
    ("scitex_dict", "scitex.dict"),
    ("scitex_str", "scitex.str"),
    ("scitex_path", "scitex.path"),
    ("scitex_os", "scitex.os"),
    ("scitex_logging", "scitex.logging"),
    ("scitex_datetime", "scitex.dt"),
    ("scitex_ml", "scitex.ml"),
    ("scitex_writer", "scitex.writer"),
    ("scitex_repro", "scitex.repro"),
    ("scitex_session", "scitex.session"),
    ("scitex_decorators", "scitex.decorators"),
    ("scitex_db", "scitex.db"),
    ("scitex_nn", "scitex.nn"),
    ("scitex_parallel", "scitex.parallel"),
    ("scitex_resource", "scitex.resource"),
    ("scitex_types", "scitex.types"),
    ("scitex_linalg", "scitex.linalg"),
    ("scitex_tex", "scitex.tex"),
    ("scitex_etc", "scitex.etc"),
    ("scitex_gists", "scitex.gists"),
    ("scitex_security", "scitex.security"),
    ("scitex_genai", "scitex.genai"),
    # plt is the three-layer entanglement (scitex_plt / figrecipe /
    # scitex.plt). Known broken — see project_plt_three_layer_entanglement
    # memory. Tracked separately, not skipped silently so it stays visible.
    pytest.param(
        "scitex_plt",
        "scitex.plt",
        marks=pytest.mark.xfail(
            reason=(
                "scitex.plt builds directly from figrecipe and skips "
                "scitex_plt re-export; needs a focused session to settle "
                "(see project_plt_three_layer_entanglement memory)."
            ),
            strict=True,
        ),
    ),
]


def _public(mod) -> set[str]:
    """Public attributes — excluding dunders, single-underscore privates,
    and the `from __future__ import annotations` symbol that's noise."""
    return {a for a in dir(mod) if not a.startswith("_") and a != "annotations"}


@pytest.mark.parametrize("peer_name,umbrella_path", PEERS)
def test_peer_public_names_are_reachable_via_umbrella(
    peer_name: str, umbrella_path: str
):
    """Every public name in the peer must be reachable via the umbrella.

    Asymmetric: the umbrella may add extras (BUNDLE_AVAILABLE, Bundle, etc.)
    The peer cannot lose names.
    """
    # Arrange
    peer = importlib.import_module(peer_name)
    umbrella = importlib.import_module(umbrella_path)
    # Act
    missing = _public(peer) - _public(umbrella)
    # Assert
    assert not missing, (
        f"{peer_name} public names not reachable via {umbrella_path}: {sorted(missing)}"
    )


# EOF
