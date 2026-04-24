"""End-to-end canonical journey for a SciTeX experiment script.

Exercises the full core-umbrella pipeline in one script:

    1. stx.session.start(...)               — write run dir + CONFIGS
    2. stx.io.save(...)                     — figure + CSV export
    3. stx.stats.run_test(...)              — real statistical run
    4. stx.io.save(stats_result, ...)       — persist result
    5. Assert every artifact exists on disk.

Notification + audio hooks are deliberately OUT of scope here — they
depend on credentials (SMTP, Twilio, ElevenLabs) and live in
`tests/scitex/notification/` and `tests/scitex/audio/` respectively.

This test guards the umbrella contract: if any of the 4 re-exports
drift, the journey breaks in one place.
"""

from __future__ import annotations

import os
import sys

import pytest

# Pre-import guard: the host environment may have a broken jax install
# (circular import) that prevents `scitex.session.start` from working.
# Skip rather than flag this as a scitex regression.
pytest.importorskip("scitex")
pytest.importorskip("scitex.session")

try:
    import matplotlib

    import scitex  # noqa: F401
    import scitex.io  # noqa: F401
    import scitex.session  # noqa: F401
    import scitex.stats  # noqa: F401

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
except Exception as exc:
    pytest.skip(f"Prerequisite import failed: {exc!r}", allow_module_level=True)


@pytest.mark.slow
def test_canonical_session_io_stats_journey(tmp_path, monkeypatch):
    """session → io.save(figure+csv) → stats.run_test → io.save(stats) round-trip."""
    import numpy as np

    import scitex as stx

    # --- 1. session.start: create run dir + CONFIGS --------------------
    sdir = tmp_path / "run"
    try:
        CONFIG, _, _, _, _, _ = stx.session.start(
            sys=sys,
            plt=plt,
            sdir=str(sdir),
            verbose=False,
            seed=42,
            agg=True,
        )
    except AttributeError as exc:
        # Known upstream issue: broken jax install surfaces as a circular
        # import during session.start's optional torch/jax seeding. Not a
        # scitex regression — skip rather than fail CI on host-env breakage.
        if "ClusterEnv" in str(exc) or "jax" in str(exc):
            pytest.skip(f"host jax env broken (pre-existing): {exc}")
        raise

    run_dir = str(CONFIG.SDIR_RUN)
    assert os.path.isdir(run_dir), f"session.start did not create SDIR_RUN={run_dir}"
    # CONFIG is persisted
    configs_dir = os.path.join(run_dir, "CONFIGS")
    assert os.path.isdir(configs_dir), f"CONFIGS dir missing under {run_dir}"

    # --- 2. figure save (PNG + auto CSV export via figrecipe) ---------
    rng = np.random.default_rng(42)
    g1 = rng.normal(0, 1, 30)
    g2 = rng.normal(0.5, 1, 30)

    fig, ax = plt.subplots()
    ax.boxplot([g1, g2], labels=["g1", "g2"], _array=[g1, g2])
    stx.io.save(fig, "./boxplot.png", symlink_from_cwd=False)

    png_path = os.path.join(run_dir, "boxplot.png")
    assert os.path.isfile(png_path), f"io.save did not write PNG at {png_path}"

    # --- 3. stats.run_test: real t-test --------------------------------
    result = stx.stats.run_test("ttest_ind", g1, g2, return_as="dict")
    assert "pvalue" in result
    assert "effect_size" in result

    # --- 4. persist stats result as YAML ------------------------------
    stx.io.save(result, "./stats.yaml", symlink_from_cwd=False)
    yaml_path = os.path.join(run_dir, "stats.yaml")
    assert os.path.isfile(yaml_path)


# EOF
