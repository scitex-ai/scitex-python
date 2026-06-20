NN Module (``stx.nn``)
======================

PyTorch neural network layers for signal processing and neuroscience
applications.

Quick Reference
---------------

.. code-block:: python

   import scitex as stx
   import torch

   # Bandpass filtering as a differentiable layer
   bpf = stx.nn.BandPassFilter(
       bands=[[4, 8], [8, 13], [13, 30]],  # theta, alpha, beta
       fs=256, seq_len=1024
   )
   filtered = bpf(signal)  # (batch, channels, 3, 1024)

   # Power spectral density
   psd = stx.nn.PSD(sample_rate=256)
   power, freqs = psd(signal)

   # Phase-amplitude coupling
   pac = stx.nn.PAC(seq_len=1024, fs=256)
   coupling = pac(signal)

Signal Processing Layers
-------------------------

**Filtering** (all differentiable):

- ``BandPassFilter(bands, fs, seq_len)`` -- Multi-band frequency filtering
- ``BandStopFilter(bands, fs, seq_len)`` -- Reject frequency bands
- ``LowPassFilter(cutoffs_hz, fs, seq_len)`` -- Anti-aliasing / smoothing
- ``HighPassFilter(cutoffs_hz, fs, seq_len)`` -- High-frequency emphasis
- ``GaussianFilter(sigma)`` -- Gaussian kernel smoothing
- ``DifferentiableBandPassFilter(...)`` -- Learnable bandpass parameters

**Spectral Analysis**:

- ``Spectrogram(sampling_rate, n_fft)`` -- STFT-based magnitude spectrogram
- ``PSD(sample_rate, prob)`` -- FFT-based power spectral density
- ``Wavelet(samp_rate, freq_scale)`` -- Continuous wavelet transform

**Phase & Coupling**:

- ``Hilbert(seq_len)`` -- Analytic signal (phase + amplitude)
- ``ModulationIndex(n_bins)`` -- Phase-amplitude coupling metric
- ``PAC(seq_len, fs, ...)`` -- Complete PAC analysis pipeline

Channel Manipulation
--------------------

- ``SwapChannels()`` -- Random channel permutation (training augmentation)
- ``DropoutChannels(dropout)`` -- Drop entire channels
- ``ChannelGainChanger(n_chs)`` -- Learnable per-channel scaling
- ``FreqGainChanger(n_bands, fs)`` -- Learnable per-band scaling

Attention & Shape
-----------------

- ``SpatialAttention(n_chs_in)`` -- Adaptive channel weighting
- ``TransposeLayer(axis1, axis2)`` -- Dimension permutation
- ``AxiswiseDropout(dropout_prob, dim)`` -- Drop entire axis

Architectures
-------------

- ``ResNet1D(n_chs, n_out, n_blks)`` -- 1D residual network
- ``BNet`` / ``BNet_Res`` -- Multi-head EEG classifier
- ``MNet1000`` -- 2D CNN feature extractor

API Reference
-------------

.. automodule:: scitex.nn
   :members:
