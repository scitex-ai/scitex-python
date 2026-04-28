#!/usr/bin/env python3
# Timestamp: "2025-04-10 12:46:06 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex_repo/src/scitex/nn/_Hilbert.py
# ----------------------------------------
import os

__FILE__ = "/home/ywatanabe/proj/scitex_repo/src/scitex/nn/_Hilbert.py"
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------
#!/usr/bin/env python

import torch  # 1.7.1
import torch.nn as nn
from torch.fft import fft, ifft


class Hilbert(nn.Module):
    def __init__(self, seq_len, dim=-1, fp16=False, in_place=False):
        super().__init__()
        self.dim = dim
        self.fp16 = fp16
        self.in_place = in_place
        self.n = seq_len
        f = torch.cat(
            [
                torch.arange(0, (self.n - 1) // 2 + 1) / float(self.n),
                torch.arange(-(self.n // 2), 0) / float(self.n),
            ]
        )
        self.register_buffer("f", f)

    def hilbert_transform(self, x):
        # n = x.shape[self.dim]

        # Create frequency dim
        # f = torch.cat(
        #     [
        #         torch.arange(0, (n - 1) // 2 + 1, device=x.device) / float(n),
        #         torch.arange(-(n // 2), 0, device=x.device) / float(n),
        #     ]
        # )

        orig_dtype = x.dtype
        # Preserve float32/float64 dtype (float64 stays float64).
        # FFT does not support torch.float16/bfloat16 or integer dtypes,
        # so only those are upcast to float32; float32/float64 pass through.
        if x.dtype not in (torch.float32, torch.float64):
            x = x.float()
        xf = fft(x, n=self.n, dim=self.dim)
        x = x.to(orig_dtype)

        # Create step function
        steepness = 50  # This value can be adjusted
        u = torch.sigmoid(
            steepness * self.f.type_as(x)
        )  # Soft step function for differentiability

        # Reshape u to broadcast along self.dim (was implicit -1 only).
        if x.ndim > 1:
            shape = [1] * x.ndim
            shape[self.dim] = self.n
            u = u.view(*shape)

        transformed = ifft(xf * 2 * u, dim=self.dim)

        return transformed

    def forward(self, x):
        if self.fp16:
            x = x.half()

        if not self.in_place:
            x = x.clone()  # Ensure that we do not modify the input in-place

        x_comp = self.hilbert_transform(x)

        pha = torch.atan2(x_comp.imag, x_comp.real)
        amp = x_comp.abs()

        assert x.shape == pha.shape == amp.shape

        out = torch.cat(
            [
                pha.unsqueeze(-1),
                amp.unsqueeze(-1),
            ],
            dim=-1,
        )

        # if self.fp16:
        #     out = (
        #         out.float()
        #     )
        #     # Optionally cast back to float for stability in subsequent operations

        if self.fp16:
            out = out.float()

        return out


if __name__ == "__main__":
    import scitex

    xx, tt, fs = scitex.dsp.demo_sig()
    xx = torch.tensor(xx)

    # Parameters
    device = "cuda"
    fp16 = True
    in_place = True

    # Initialization
    m = Hilbert(xx.shape[-1], fp16=fp16, in_place=in_place).to(device)

    # Calculation
    xx = xx.to(device)
    y = m(xx)

# EOF
