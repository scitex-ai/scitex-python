#!/usr/bin/env python3
"""SciTeX DSP umbrella — thin re-export of the ``scitex_dsp`` standalone.

Per `general/01_ecosystem_05_re-export.md`, the umbrella is a bridge:
no original logic, just named re-exports of the standalone's public
API. This keeps `scitex.dsp.X` and `scitex_dsp.X` resolving to the
same objects — discoverable through both namespaces.
"""

import sys as _sys

import scitex_dsp as _real
from scitex_dsp import (
    add_noise,
    band_powers,
    crop,
    demo_sig,
    detect_ripples,
    ensure_3d,
    example,
    filt,
    get_eeg_pos,
    hilbert,
    list_and_select_device,
    modulation_index,
    norm,
    pac,
    params,
    psd,
    reference,
    resample,
    time,
    to_segments,
    to_sktime_df,
    utils,
    wavelet,
)

# Allow `from scitex.dsp.<sub> import …` for every standalone submodule
# (e.g. `from scitex.dsp.utils.pac import …`). Without these aliases,
# Python's import resolver looks at `scitex/dsp/__path__` only, which
# in this thin-bridge package contains no real submodules.
for _name in list(_sys.modules):
    if _name == "scitex_dsp" or _name.startswith("scitex_dsp."):
        _alias = "scitex.dsp" + _name[len("scitex_dsp") :]
        _sys.modules.setdefault(_alias, _sys.modules[_name])
del _sys, _name, _alias, _real

__all__ = [
    "add_noise",
    "band_powers",
    "crop",
    "demo_sig",
    "detect_ripples",
    "ensure_3d",
    "example",
    "filt",
    "get_eeg_pos",
    "hilbert",
    "list_and_select_device",
    "modulation_index",
    "norm",
    "pac",
    "params",
    "psd",
    "reference",
    "resample",
    "time",
    "to_segments",
    "to_sktime_df",
    "wavelet",
]
