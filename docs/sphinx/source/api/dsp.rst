DSP Module (``stx.dsp``)
========================

Digital signal processing tools for filtering, spectral analysis,
and time-frequency decomposition.

Quick Reference
---------------

.. code-block:: python

    import scitex as stx
    import numpy as np

    # Generate test signal
    fs = 1000  # Hz
    t = np.arange(0, 1, 1/fs)
    signal = np.sin(2 * np.pi * 10 * t) + 0.5 * np.sin(2 * np.pi * 50 * t)

    # Filtering
    filtered = stx.dsp.filt.bandpass(signal, fs=fs, low=5, high=30)
    low_pass = stx.dsp.filt.lowpass(signal, fs=fs, cutoff=20)
    high_pass = stx.dsp.filt.highpass(signal, fs=fs, cutoff=5)

    # Power spectral density
    freqs, psd = stx.dsp.psd(signal, fs=fs)

    # Band powers
    powers = stx.dsp.band_powers(signal, fs=fs, bands={
        "delta": (1, 4),
        "theta": (4, 8),
        "alpha": (8, 13),
        "beta": (13, 30),
    })

    # Hilbert transform (analytic signal)
    analytic = stx.dsp.hilbert(signal)
    amplitude = np.abs(analytic)
    phase = np.angle(analytic)

    # Wavelet decomposition
    coeffs = stx.dsp.wavelet(signal, fs=fs, freqs=np.arange(1, 50))

Available Functions
-------------------

**Filtering** (``stx.dsp.filt``)

- ``bandpass(signal, fs, low, high)``
- ``lowpass(signal, fs, cutoff)``
- ``highpass(signal, fs, cutoff)``
- ``notch(signal, fs, freq)``

**Spectral Analysis**

- ``psd(signal, fs)`` -- Power spectral density
- ``band_powers(signal, fs, bands)`` -- Power in frequency bands
- ``wavelet(signal, fs, freqs)`` -- Continuous wavelet transform

**Time-Frequency**

- ``hilbert(signal)`` -- Analytic signal via Hilbert transform
- ``pac(signal, fs)`` -- Phase-amplitude coupling

**Utilities**

- ``demo_sig(fs, duration)`` -- Generate demo signals for testing
- ``crop(signal, start, end, fs)`` -- Crop signal to time range
- ``detect_ripples(signal, fs)`` -- Detect sharp-wave ripples

API Reference
-------------

.. automodule:: scitex.dsp
   :members:
