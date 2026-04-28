#!/usr/bin/env python3
# Time-stamp: "2024-11-04 02:07:11 (ywatanabe)"
# File: ./scitex_repo/src/scitex/dsp/_hilbert.py

"""
This script does XYZ.
"""

import sys

import matplotlib.pyplot as plt

from scitex.decorators import signal_fn
from scitex.nn._Hilbert import Hilbert


# Functions
@signal_fn
def hilbert(
    x,
    dim=-1,
):
    seq_len = x.shape[dim]
    if seq_len == 0:
        empty = (
            x[..., :0]
            if dim in (-1, x.ndim - 1)
            else x.swapaxes(dim, -1)[..., :0].swapaxes(dim, -1)
        )
        return empty, empty
    y = Hilbert(seq_len, dim=dim)(x)
    return y[..., 0], y[..., 1]


if __name__ == "__main__":
    import scitex

    # Start
    CONFIG, sys.stdout, sys.stderr, plt, CC = scitex.session.start(sys, plt)

    # Parameters
    T_SEC = 1.0
    FS = 400
    SIG_TYPE = "chirp"

    # Demo signal
    xx, tt, fs = scitex.dsp.demo_sig(t_sec=T_SEC, fs=FS, sig_type=SIG_TYPE)

    # Main
    pha, amp = hilbert(
        xx,
        dim=-1,
    )
    # (32, 19, 1280, 2)

    # Plots
    fig, axes = scitex.plt.subplots(nrows=2, sharex=True)
    fig.suptitle("Hilbert Transformation")

    axes[0].plot(tt, xx[0, 0], label=SIG_TYPE)
    axes[0].plot(tt, amp[0, 0], label="Amplidue")
    axes[0].legend()
    # axes[0].set_xlabel("Time [s]")
    axes[0].set_ylabel("Amplitude [?V]")

    axes[1].plot(tt, pha[0, 0], label="Phase")
    axes[1].legend()

    axes[1].set_xlabel("Time [s]")
    axes[1].set_ylabel("Phase [rad]")

    # plt.show()
    scitex.io.save(fig, "traces.png")

    # Close
    scitex.session.close(CONFIG)

# EOF

"""
/home/ywatanabe/proj/entrance/scitex/dsp/_hilbert.py
"""


# EOF
