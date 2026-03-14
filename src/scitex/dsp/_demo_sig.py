#!/usr/bin/env python3
# Time-stamp: "2024-11-06 01:45:32 (ywatanabe)"
# File: ./scitex_repo/src/scitex/dsp/_demo_sig.py

import random
import sys
import warnings

import matplotlib.pyplot as plt
import numpy as np
from scipy.signal import chirp

try:
    import mne
    from mne.datasets import sample

    MNE_AVAILABLE = True
except ImportError:
    MNE_AVAILABLE = False
    mne = None
    sample = None

try:
    from ripple_detection.simulate import simulate_LFP, simulate_time

    RIPPLE_DETECTION_AVAILABLE = True
except ImportError:
    RIPPLE_DETECTION_AVAILABLE = False
    simulate_LFP = None
    simulate_time = None

try:
    from tensorpac.signals import pac_signals_wavelet

    TENSORPAC_AVAILABLE = True
except ImportError:
    TENSORPAC_AVAILABLE = False
    pac_signals_wavelet = None

from scitex.io import load_configs

# Config
CONFIG = load_configs(verbose=False)


def _check_mne():
    if not MNE_AVAILABLE:
        raise ImportError(
            "MNE-Python is not installed. Please install with: pip install mne"
        )


def _check_ripple_detection():
    if not RIPPLE_DETECTION_AVAILABLE:
        raise ImportError(
            "ripple_detection is not installed. Please install with: pip install ripple_detection"
        )


def _check_tensorpac():
    if not TENSORPAC_AVAILABLE:
        raise ImportError(
            "tensorpac is not installed. Please install with: pip install tensorpac"
        )


# Functions
def demo_sig(
    sig_type="periodic",
    batch_size=8,
    n_chs=19,
    n_segments=20,
    t_sec=4,
    fs=512,
    freqs_hz=None,
    verbose=False,
):
    """
    Generate demo signals for various signal types.

    Parameters
    ----------
    sig_type : str, optional
        Type of signal to generate. Options are "uniform", "gauss", "periodic", "chirp", "ripple", "meg", "tensorpac", "pac".
        Default is "periodic".
    batch_size : int, optional
        Number of batches to generate. Default is 8.
    n_chs : int, optional
        Number of channels. Default is 19.
    n_segments : int, optional
        Number of segments for tensorpac and pac signals. Default is 20.
    t_sec : float, optional
        Duration of the signal in seconds. Default is 4.
    fs : int, optional
        Sampling frequency in Hz. Default is 512.
    freqs_hz : list or None, optional
        List of frequencies in Hz for periodic signals. If None, random frequencies will be used.
    verbose : bool, optional
        If True, print additional information. Default is False.

    Returns
    -------
    tuple
        A tuple containing:
        - np.ndarray: Generated signal(s) with shape (batch_size, n_chs, time_samples) or (batch_size, n_chs, n_segments, time_samples) for tensorpac and pac signals.
        - np.ndarray: Time array.
        - int: Sampling frequency.
    """
    assert sig_type in [
        "uniform",
        "gauss",
        "periodic",
        "chirp",
        "ripple",
        "meg",
        "tensorpac",
        "pac",
    ]
    tt = np.linspace(0, t_sec, int(t_sec * fs), endpoint=False)

    if sig_type == "uniform":
        return (
            np.random.uniform(low=-0.5, high=0.5, size=(batch_size, n_chs, len(tt))),
            tt,
            fs,
        )

    elif sig_type == "gauss":
        return np.random.randn(batch_size, n_chs, len(tt)), tt, fs

    elif sig_type == "meg":
        return (
            _demo_sig_meg(
                batch_size=batch_size,
                n_chs=n_chs,
                t_sec=t_sec,
                fs=fs,
                verbose=verbose,
            ).astype(np.float32)[..., : len(tt)],
            tt,
            fs,
        )

    elif sig_type == "tensorpac":
        xx, tt = _demo_sig_tensorpac(
            batch_size=batch_size,
            n_chs=n_chs,
            n_segments=n_segments,
            t_sec=t_sec,
            fs=fs,
        )
        return xx.astype(np.float32)[..., : len(tt)], tt, fs

    elif sig_type == "pac":
        xx = _demo_sig_pac(
            batch_size=batch_size,
            n_chs=n_chs,
            n_segments=n_segments,
            t_sec=t_sec,
            fs=fs,
        )
        return xx.astype(np.float32)[..., : len(tt)], tt, fs

    else:
        fn_1d = {
            "periodic": _demo_sig_periodic_1d,
            "chirp": _demo_sig_chirp_1d,
            "ripple": _demo_sig_ripple_1d,
        }.get(sig_type)

        return (
            (
                np.array(
                    [
                        fn_1d(
                            t_sec=t_sec,
                            fs=fs,
                            freqs_hz=freqs_hz,
                            verbose=verbose,
                        )
                        for _ in range(int(batch_size * n_chs))
                    ]
                )
                .reshape(batch_size, n_chs, -1)
                .astype(np.float32)[..., : len(tt)]
            ),
            tt,
            fs,
        )


def _demo_sig_pac(
    batch_size=8,
    n_chs=19,
    t_sec=4,
    fs=512,
    f_pha=10,
    f_amp=100,
    noise=0.8,
    n_segments=20,
    verbose=False,
):
    """
    Generate a demo signal with phase-amplitude coupling.

    Parameters
    ----------
        batch_size (int): Number of batches.
        n_chs (int): Number of channels.
        t_sec (int): Duration of the signal in seconds.
        fs (int): Sampling frequency.
        f_pha (float): Frequency of the phase-modulating signal.
        f_amp (float): Frequency of the amplitude-modulated signal.
        noise (float): Noise level added to the signal.
        n_segments (int): Number of segments.
        verbose (bool): If True, print additional information.

    Returns
    -------
        np.array: Generated signals with shape (batch_size, n_chs, n_segments, seq_len).
    """
    seq_len = t_sec * fs
    t = np.arange(seq_len) / fs
    if verbose:
        print(f"Generating signal with length: {seq_len}")

    # Create empty array to store the signals
    signals = np.zeros((batch_size, n_chs, n_segments, seq_len))

    for b in range(batch_size):
        for ch in range(n_chs):
            for seg in range(n_segments):
                # Phase signal
                theta = np.sin(2 * np.pi * f_pha * t)
                # Amplitude envelope
                amplitude_env = 1 + np.sin(2 * np.pi * f_amp * t)
                # Combine phase and amplitude modulation
                signal = theta * amplitude_env
                # Add Gaussian noise
                signal += noise * np.random.randn(seq_len)
                signals[b, ch, seg, :] = signal

    return signals


def _demo_sig_tensorpac(
    batch_size=8,
    n_chs=19,
    t_sec=4,
    fs=512,
    f_pha=10,
    f_amp=100,
    noise=0.8,
    n_segments=20,
    verbose=False,
):
    _check_tensorpac()
    n_times = int(t_sec * fs)
    x_2d, tt = pac_signals_wavelet(
        sf=fs,
        f_pha=f_pha,
        f_amp=f_amp,
        noise=noise,
        n_epochs=n_segments,
        n_times=n_times,
    )
    x_3d = np.stack([x_2d for _ in range(batch_size)], axis=0)
    x_4d = np.stack([x_3d for _ in range(n_chs)], axis=1)
    return x_4d, tt


def _demo_sig_meg(batch_size=8, n_chs=19, t_sec=10, fs=512, verbose=False, **kwargs):
    _check_mne()
    data_path = sample.data_path()
    meg_path = data_path / "MEG" / "sample"
    raw_fname = meg_path / "sample_audvis_raw.fif"
    fwd_fname = meg_path / "sample_audvis-meg-eeg-oct-6-fwd.fif"

    # Load real data as the template
    raw = mne.io.read_raw_fif(raw_fname, verbose=verbose)
    raw = raw.crop(tmax=t_sec, verbose=verbose)
    raw = raw.resample(fs, verbose=verbose)
    raw.set_eeg_reference(projection=True, verbose=verbose)

    return raw.get_data(
        picks=raw.ch_names[: batch_size * n_chs], verbose=verbose
    ).reshape(batch_size, n_chs, -1)


def _demo_sig_periodic_1d(t_sec=10, fs=512, freqs_hz=None, verbose=False, **kwargs):
    """Returns a demo signal with the shape (t_sec*fs,)."""
    if freqs_hz is None:
        n_freqs = random.randint(1, 5)
        freqs_hz = np.random.permutation(np.arange(fs))[:n_freqs]
        if verbose:
            print(f"freqs_hz was randomly determined as {freqs_hz}")

    n = int(t_sec * fs)
    t = np.linspace(0, t_sec, n, endpoint=False)

    summed = np.array(
        [
            np.random.rand() * np.sin((f_hz * t + np.random.rand()) * (2 * np.pi))
            for f_hz in freqs_hz
        ]
    ).sum(axis=0)
    return summed


def _demo_sig_chirp_1d(
    t_sec=10, fs=512, low_hz=None, high_hz=None, verbose=False, **kwargs
):
    if low_hz is None:
        low_hz = random.randint(1, 20)
        if verbose:
            warnings.warn(f"low_hz was randomly determined as {low_hz}.")

    if high_hz is None:
        high_hz = random.randint(100, 1000)
        if verbose:
            warnings.warn(f"high_hz was randomly determined as {high_hz}.")

    n = int(t_sec * fs)
    t = np.linspace(0, t_sec, n, endpoint=False)
    x = chirp(t, low_hz, t[-1], high_hz)
    x *= 1.0 + 0.5 * np.sin(2.0 * np.pi * 3.0 * t)
    return x


def _demo_sig_ripple_1d(t_sec=10, fs=512, **kwargs):
    _check_ripple_detection()
    n_samples = t_sec * fs
    t = simulate_time(n_samples, fs)
    n_ripples = random.randint(1, 5)
    mid_time = np.random.permutation(t)[:n_ripples]
    return simulate_LFP(t, mid_time, noise_amplitude=1.2, ripple_amplitude=5)


if __name__ == "__main__":
    import scitex

    # Start
    CONFIG, sys.stdout, sys.stderr, plt, CC = scitex.session.start(sys, plt)
    import scitex

    SIG_TYPES = [
        "uniform",
        "gauss",
        "periodic",
        "chirp",
        "meg",
        "ripple",
        "tensorpac",
        "pac",
    ]

    i_batch, i_ch, i_segment = 0, 0, 0
    fig, axes = scitex.plt.subplots(nrows=len(SIG_TYPES))
    for ax, (i_sig_type, sig_type) in zip(axes, enumerate(SIG_TYPES)):
        xx, tt, fs = demo_sig(sig_type=sig_type)
        if sig_type not in ["tensorpac", "pac"]:
            ax.plot(tt, xx[i_batch, i_ch], label=sig_type)
        else:
            ax.plot(tt, xx[i_batch, i_ch, i_segment], label=sig_type)
        ax.legend(loc="upper left")
    fig.suptitle("Demo signals")
    fig.supxlabel("Time [s]")
    fig.supylabel("Amplitude [?V]")
    scitex.io.save(fig, "traces.png")

    # Close
    scitex.session.close(CONFIG)

# EOF

"""
/home/ywatanabe/proj/entrance/scitex/dsp/_demo_sig.py
"""

# EOF
