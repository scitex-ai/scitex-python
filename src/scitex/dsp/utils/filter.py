#!/usr/bin/env python3
# Time-stamp: "2024-11-03 07:24:43 (ywatanabe)"
# File: ./scitex_repo/src/scitex/dsp/utils/filter.py

import matplotlib.pyplot as plt
import numpy as np
from scipy.signal import firwin, freqz

from scitex.decorators import numpy_fn
from scitex.gen._to_even import to_even


@numpy_fn
def design_filter(sig_len, fs, low_hz=None, high_hz=None, cycle=3, is_bandstop=False):
    """
    Designs a Finite Impulse Response (FIR) filter based on the specified parameters.

    Arguments:
    - sig_len (int): Length of the signal for which the filter is being designed.
    - fs (int): Sampling frequency of the signal.
    - low_hz (float, optional): Low cutoff frequency for the filter. Required for lowpass and bandpass filters.
    - high_hz (float, optional): High cutoff frequency for the filter. Required for highpass and bandpass filters.
    - cycle (int, optional): Number of cycles to use in determining the filter order. Defaults to 3.
    - is_bandstop (bool, optional): Specifies if the filter should be a bandstop filter. Defaults to False.

    Returns
    -------
    - The coefficients of the designed FIR filter.

    Raises
    ------
    - FilterParameterError: If the provided parameters are invalid.
    """

    class FilterParameterError(Exception):
        """Custom exception for invalid filter parameters."""

        pass

    def estimate_filter_type(low_hz=None, high_hz=None, is_bandstop=False):
        """
        Estimates the filter type based on the provided low and high cutoff frequencies,
        and whether a bandstop filter is desired. Raises an exception for invalid configurations.
        """
        if low_hz is not None and low_hz < 0:
            raise FilterParameterError("low_hz must be non-negative.")
        if high_hz is not None and high_hz < 0:
            raise FilterParameterError("high_hz must be non-negative.")
        if low_hz is not None and high_hz is not None and low_hz >= high_hz:
            raise FilterParameterError(
                "low_hz must be less than high_hz for valid configurations."
            )

        if low_hz is not None and high_hz is not None:
            return "bandstop" if is_bandstop else "bandpass"
        elif low_hz is not None:
            return "lowpass"
        elif high_hz is not None:
            return "highpass"
        else:
            raise FilterParameterError(
                "At least one of low_hz or high_hz must be provided."
            )

    def determine_cutoff_frequencies(filter_mode, low_hz, high_hz):
        if filter_mode in ["lowpass", "highpass"]:
            cutoff = low_hz if filter_mode == "lowpass" else high_hz
        else:  # 'bandpass' or 'bandstop'
            cutoff = [low_hz, high_hz]
        return cutoff

    def determine_low_freq(filter_mode, low_hz, high_hz):
        if filter_mode in ["lowpass", "bandstop"]:
            low_freq = low_hz
        else:  # 'highpass' or 'bandpass'
            low_freq = high_hz if filter_mode == "highpass" else min(low_hz, high_hz)
        return low_freq

    def determine_order(filter_mode, fs, low_freq, sig_len, cycle):
        order = cycle * int(fs // low_freq)
        if 3 * order < sig_len:
            order = (sig_len - 1) // 3
        order = to_even(order)
        return order

    # fs may arrive as a torch tensor (when called from PAC.init_bandpass with
    # a numeric fs that the @signal_fn decorator wraps); int(tensor) only
    # works for 0-dim. Coerce via .item() when available.
    fs = int(fs.item()) if hasattr(fs, "item") else int(fs)
    low_hz = float(low_hz) if low_hz is not None else low_hz
    high_hz = float(high_hz) if high_hz is not None else high_hz
    filter_mode = estimate_filter_type(low_hz, high_hz, is_bandstop)
    cutoff = determine_cutoff_frequencies(filter_mode, low_hz, high_hz)
    low_freq = determine_low_freq(filter_mode, low_hz, high_hz)
    order = determine_order(filter_mode, fs, low_freq, sig_len, cycle)
    numtaps = order + 1

    try:
        h = firwin(
            numtaps=numtaps,
            cutoff=cutoff,
            pass_zero=(filter_mode in ["highpass", "bandstop"]),
            window="hamming",
            fs=fs,
            scale=True,
        )
    except Exception as e:
        print(e)
        import ipdb

        ipdb.set_trace()

    return h


@numpy_fn
def plot_filter_responses(filter, fs, worN=8000, title=None):
    """
    Plots the impulse and frequency response of an FIR filter using numpy arrays.

    Parameters
    ----------
    - filter_coeffs (numpy.ndarray): The filter coefficients as a numpy array.
    - fs (int): The sampling frequency in Hz.
    - title (str, optional): The title of the plot. Defaults to None.

    Returns
    -------
    - matplotlib.figure.Figure: The figure object containing the impulse and frequency response plots.
    """
    import scitex

    ww, hh = freqz(filter, worN=worN, fs=fs)

    fig, axes = scitex.plt.subplots(ncols=2)
    fig.suptitle(title)

    # Impulse Responses of FIR Filter
    ax = axes[0]
    ax.plot(filter)
    ax.set_title("Impulse Responses of FIR Filter")
    ax.set_xlabel("Tap Number")
    ax.set_ylabel("Amplitude")

    # Frequency Response of FIR Filter
    ax = axes[1]
    ax.plot(ww, 20 * np.log10(abs(hh) + 1e-5))
    ax.set_title("Frequency Response of FIR Filter")
    ax.set_xlabel("Frequency [Hz]")
    ax.set_ylabel("Gain [dB]")

    return fig


if __name__ == "__main__":
    import scitex

    # Example usage
    xx, tt, fs = scitex.dsp.demo_sig()
    batch_size, n_chs, seq_len = xx.shape

    lp_filter = design_filter(seq_len, fs, low_hz=30, high_hz=None)
    hp_filter = design_filter(seq_len, fs, low_hz=None, high_hz=70)
    bp_filter = design_filter(seq_len, fs, low_hz=30, high_hz=70)
    bs_filter = design_filter(seq_len, fs, low_hz=30, high_hz=70, is_bandstop=True)

    fig = plot_filter_responses(lp_filter, fs, title="Lowpass Filter")
    fig = plot_filter_responses(hp_filter, fs, title="Highpass Filter")
    fig = plot_filter_responses(bp_filter, fs, title="Bandpass Filter")
    fig = plot_filter_responses(bs_filter, fs, title="Bandstop Filter")

    # Figure
    fig, axes = plt.subplots(nrows=4, ncols=2)

    # Time domain expressions??
    axes[0, 0].plot(lp_filter, label="Lowpass Filter")
    axes[1, 0].plot(hp_filter, label="Highpass Filter")
    axes[2, 0].plot(bp_filter, label="Bandpass Filter")
    axes[3, 0].plot(bs_filter, label="Bandstop Filter")
    # fig.suptitle("Impulse Responses of FIR Filter")
    # fig.supxlabel("Tap Number")
    # fig.supylabel("Amplitude")
    # fig.show()

    # Frequency response of the filters
    w, h_lp = freqz(lp_filter, worN=8000, fs=fs)
    w, h_hp = freqz(hp_filter, worN=8000, fs=fs)
    w, h_bp = freqz(bp_filter, worN=8000, fs=fs)
    w, h_bs = freqz(bs_filter, worN=8000, fs=fs)

    # Plotting the frequency response
    axes[0, 1].plot(w, 20 * np.log10(abs(h_lp)), label="Lowpass Filter")
    axes[1, 1].plot(w, 20 * np.log10(abs(h_hp)), label="Highpass Filter")
    axes[2, 1].plot(w, 20 * np.log10(abs(h_bp)), label="Bandpass Filter")
    axes[3, 1].plot(w, 20 * np.log10(abs(h_bs)), label="Bandstop Filter")
    # plt.title("Frequency Response of FIR Filters")
    # plt.xlabel("Frequency (Hz)")
    # plt.ylabel("Gain (dB)")
    # plt.grid(True)
    # plt.legend(loc="best")
    # plt.show()
    fig.tight_layout()
    plt.show()

# @torch_fn
# def bandpass(x, filt):
#     assert x.ndim == 3
#     xf = F.conv1d(
#         x.reshape(-1, x.shape[-1]).unsqueeze(1),
#         filt.unsqueeze(0).unsqueeze(0),
#         padding="same",
#     ).reshape(*x.shape)
#     assert x.shape == xf.shape
#     return xf

# def define_bandpass_filters(seq_len, fs, freq_bands, cycle=3):
#     """
#     Defines Finite Impulse Response (FIR) filters.
#     b: The filter coefficients (or taps) of the FIR filters
#     a: The denominator coefficients of the filter's transfer function.  However, FIR filters have a transfer function with a denominator equal to 1 (since they are all-zero filters with no poles).
#     """
#     # Parameters
#     n_freqs = len(freq_bands)
#     nyq = fs / 2.0

#     bs = []
#     for ll, hh in freq_bands:
#         wn = np.array([ll, hh]) / nyq
#         order = define_fir_order(fs, seq_len, ll, cycle=cycle)
#         bs.append(fir1(order, wn)[0])
#     return bs

# def define_fir_order(fs, sizevec, flow, cycle=3):
#     """
#     Calculate filter order.
#     """
#     if cycle is None:
#         filtorder = 3 * np.fix(fs / flow)
#     else:
#         filtorder = cycle * (fs // flow)

#         if sizevec < 3 * filtorder:
#             filtorder = (sizevec - 1) // 3

#     return int(filtorder)

# def n_odd_fcn(f, o, w, l):
#     """Odd case."""
#     # Variables :
#     b0 = 0
#     m = np.array(range(int(l + 1)))
#     k = m[1 : len(m)]
#     b = np.zeros(k.shape)

#     # Run Loop :
#     for s in range(0, len(f), 2):
#         m = (o[s + 1] - o[s]) / (f[s + 1] - f[s])
#         b1 = o[s] - m * f[s]
#         b0 = b0 + (
#             b1 * (f[s + 1] - f[s])
#             + m / 2 * (f[s + 1] * f[s + 1] - f[s] * f[s])
#         ) * abs(np.square(w[round((s + 1) / 2)]))
#         b = b + (
#             m
#             / (4 * np.pi * np.pi)
#             * (
#                 np.cos(2 * np.pi * k * f[s + 1])
#                 - np.cos(2 * np.pi * k * f[s])
#             )
#             / (k * k)
#         ) * abs(np.square(w[round((s + 1) / 2)]))
#         b = b + (
#             f[s + 1] * (m * f[s + 1] + b1) * np.sinc(2 * k * f[s + 1])
#             - f[s] * (m * f[s] + b1) * np.sinc(2 * k * f[s])
#         ) * abs(np.square(w[round((s + 1) / 2)]))

#     b = np.insert(b, 0, b0)
#     a = (np.square(w[0])) * 4 * b
#     a[0] = a[0] / 2
#     aud = np.flipud(a[1 : len(a)]) / 2
#     a2 = np.insert(aud, len(aud), a[0])
#     h = np.concatenate((a2, a[1:] / 2))

#     return h

# def n_even_fcn(f, o, w, l):
#     """Even case."""
#     # Variables :
#     k = np.array(range(0, int(l) + 1, 1)) + 0.5
#     b = np.zeros(k.shape)

#     # # Run Loop :
#     for s in range(0, len(f), 2):
#         m = (o[s + 1] - o[s]) / (f[s + 1] - f[s])
#         b1 = o[s] - m * f[s]
#         b = b + (
#             m
#             / (4 * np.pi * np.pi)
#             * (
#                 np.cos(2 * np.pi * k * f[s + 1])
#                 - np.cos(2 * np.pi * k * f[s])
#             )
#             / (k * k)
#         ) * abs(np.square(w[round((s + 1) / 2)]))
#         b = b + (
#             f[s + 1] * (m * f[s + 1] + b1) * np.sinc(2 * k * f[s + 1])
#             - f[s] * (m * f[s] + b1) * np.sinc(2 * k * f[s])
#         ) * abs(np.square(w[round((s + 1) / 2)]))

#     a = (np.square(w[0])) * 4 * b
#     h = 0.5 * np.concatenate((np.flipud(a), a))

#     return h

# def firls(n, f, o):
#     # Variables definition :
#     w = np.ones(round(len(f) / 2))
#     n += 1
#     f /= 2
#     lo = (n - 1) / 2

#     nodd = bool(n % 2)

#     if nodd:  # Odd case
#         h = n_odd_fcn(f, o, w, lo)
#     else:  # Even case
#         h = n_even_fcn(f, o, w, lo)

#     return h

# def fir1(n, wn):
#     # Variables definition :
#     nbands = len(wn) + 1
#     ff = np.array((0, wn[0], wn[0], wn[1], wn[1], 1))

#     f0 = np.mean(ff[2:4])
#     lo = n + 1

#     mags = np.array(range(nbands)).reshape(1, -1) % 2
#     aa = np.ravel(np.tile(mags, (2, 1)), order="F")

#     # Get filter coefficients :
#     h = firls(lo - 1, ff, aa)

#     # Apply a window to coefficients :
#     wind = np.hamming(lo)
#     b = h * wind
#     c = np.exp(-1j * 2 * np.pi * (f0 / 2) * np.array(range(lo)))
#     b /= abs(c @ b)

#     return b, 1

# def apply_filters(x, filts):
#     """
#     x: (batch_size, n_chs, seq_len)
#     filts: (n_filts, seq_len_filt)
#     """
#     assert x.ndims == 3
#     assert filts.ndims == 2
#     batch_size, n_chs, n_time = x.shape
#     x = x.reshape(-1, x.shape[-1]).unsqueeze(1)
#     filts = filts.unsqueeze(1)
#     n_filts = len(filts)
#     return F.conv1d(x, filts, padding="same").reshape(
#         batch_size, n_chs, n_filts, n_time
#     )

# if __name__ == "__main__":
#     import torch
#     import torch.nn.functional as F

#     plt, CC = scitex.plt.configure_mpl(plt)

#     # Demo Signal
#     freqs_hz = [10, 30, 100]
#     xx, tt, fs = scitex.dsp.demo_sig(freqs_hz=freqs_hz, sig_type="periodic")
#     x = xx

#     seq_len = x.shape[-1]
#     freq_bands = np.array([[20, 70], [3.0, 4.0]])

#     # Plots the figure
#     fig, ax = scitex.plt.subplots()
#     # ax.plot(b, label="bandpass filter")

#     # Bandpass Filtering
#     filters = define_bandpass_filters(seq_len, fs, freq_bands, cycle=3)
#     i_filt = 0
#     # xf = bandpass(xx, filters[i_filt])

#     # Plots the signals
#     fig, axes = scitex.plt.subplots(nrows=2, sharex=True, sharey=True)
#     axes[0].plot(tt, xx[0, 0], label="orig")
#     axes[1].plot(tt, xf[0, 0], label="orig")
#     [ax.legend(loc="upper left") for ax in axes]

#     # Plots PSDs
#     psd_xx, ff_xx = scitex.dsp.psd(xx.numpy(), fs)
#     psd_xf, ff_xf = scitex.dsp.psd(xf.numpy(), fs)

#     fig, axes = scitex.plt.subplots(nrows=2, sharex=True, sharey=True)
#     axes[0].plot(ff_xx, psd_xx[0, 0], label="orig")
#     axes[1].plot(ff_xf, psd_xf[0, 0], label="filted")
#     [ax.legend(loc="upper left") for ax in axes]
#     plt.show()

#     # Multiple Filters in a parallel computation
#     x = torch.randn(33, 32, 30)
#     filters = torch.randn(20, 5)

#     y = apply_filters(x, filters)
#     print(y.shape)  # (33, 32, 20, 30)

# EOF
