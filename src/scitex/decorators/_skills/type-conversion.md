---
name: stx.decorators — Type Conversion
description: Automatic input-type conversion decorators (numpy_fn, torch_fn, pandas_fn, xarray_fn, signal_fn) that convert function inputs to a target array type and convert outputs back to the original caller type.
---

# Type Conversion Decorators

These decorators convert function inputs to a specific array type, run the function, then convert the output back to whatever type the caller passed in. Each decorator is a no-argument decorator applied directly to a function definition.

## Decorators

### `numpy_fn`

```python
from scitex.decorators import numpy_fn

@numpy_fn
def my_func(arr):
    # arr is guaranteed to be np.ndarray here
    return arr.mean(axis=0)
```

**Signature:** `numpy_fn(func: Callable) -> Callable`

**Input conversion (all positional args):**
| Caller type | Converted to |
|---|---|
| `list` | `np.ndarray` |
| `torch.Tensor` | `np.ndarray` via `.detach().cpu().numpy()` |
| `pd.DataFrame` | `np.ndarray` via `.to_numpy().squeeze()` |
| `pd.Series` | `np.ndarray` via `.to_numpy().squeeze()` |
| `xr.DataArray` | `np.ndarray` via `np.array(data)` |
| `int`, `float`, `str`, `None` | passed through unchanged |
| `tuple`/`list` of `int` | passed through (dimension tuples) |

**Output conversion** — when result is `np.ndarray` and first arg was:
| Original type | Output type |
|---|---|
| `list` | `list` via `.tolist()` |
| `torch.Tensor` | `torch.Tensor` via `torch.tensor(result)` |
| `pd.DataFrame` | `pd.DataFrame` |
| `pd.Series` | `pd.Series` |
| `np.ndarray` | `np.ndarray` (unchanged) |

**`axis`/`dim` parameter translation:** `dim` kwargs are renamed to `axis` so numpy functions receive the correct parameter name.

**Nested decorator guard:** Uses `is_nested_decorator()` stack inspection. If already inside a type-conversion wrapper, conversion is skipped to avoid double-conversion.

---

### `torch_fn`

```python
from scitex.decorators import torch_fn

@torch_fn
def my_func(tensor, dim=None):
    # tensor is guaranteed to be torch.Tensor here
    return tensor.mean(dim=dim)
```

**Signature:** `torch_fn(func: Callable) -> Callable`

**Input conversion:** same types as `numpy_fn` but targets `torch.Tensor`.

- Automatically moves tensors to `cuda` when `torch.cuda.is_available()` is True.
- Emits `ConversionWarning` (via `_converters.ConversionWarning`) once per unique conversion (LRU-cached) when CUDA is used.
- `axis` kwargs are renamed to `dim` so torch functions receive the correct parameter name.
- Preserves `tuple`/`list` of integers (e.g., `dim=(0, 1)`) unchanged.

**Output conversion** — when result is `torch.Tensor` and first arg was:
| Original type | Output type |
|---|---|
| `list` | `list` via `.detach().cpu().numpy().tolist()` |
| `np.ndarray` | `np.ndarray` via `.detach().cpu().numpy()` |
| `pd.DataFrame` | `pd.DataFrame` |
| `pd.Series` | `pd.Series` |
| `xr.DataArray` | `xr.DataArray` |
| `torch.Tensor` | `torch.Tensor` (unchanged) |

---

### `pandas_fn`

```python
from scitex.decorators import pandas_fn

@pandas_fn
def my_func(df):
    # df is guaranteed to be pd.DataFrame here
    return df.describe()
```

**Signature:** `pandas_fn(func: Callable) -> Callable`

**Input conversion targets `pd.DataFrame`:**
| Caller type | Converted to |
|---|---|
| `pd.Series` | `pd.DataFrame(series)` |
| `np.ndarray` | `pd.DataFrame(array)` |
| `list` | `pd.DataFrame(list)` (best-effort) |
| `torch.Tensor` | `pd.DataFrame(tensor.detach().cpu().numpy())` |
| `xr.DataArray` | `pd.DataFrame(data.values)` |
| `int`, `float`, `str` | passed through unchanged (scalars not wrapped) |

**Output conversion** — when result is `pd.DataFrame` and first arg was:
| Original type | Output type |
|---|---|
| `list` | `list` via `.values.tolist()` |
| `np.ndarray` | `np.ndarray` via `.values` |
| `torch.Tensor` | `torch.Tensor` via `torch.tensor(result.values)` |
| `pd.Series` | `pd.Series` (first column) |
| `xr.DataArray` | `xr.DataArray(result.values)` |
| `pd.DataFrame` | `pd.DataFrame` (unchanged) |

---

### `xarray_fn`

```python
from scitex.decorators import xarray_fn

@xarray_fn
def my_func(da):
    # da is guaranteed to be xr.DataArray here
    return da.mean(dim="time")
```

**Signature:** `xarray_fn(func: Callable) -> Callable`

**Input conversion targets `xr.DataArray`.**

**Strict assertion:** Unlike the other converters, `xarray_fn` asserts every positional arg is an `xr.DataArray` after conversion. Any unconvertible argument raises `AssertionError`.

**Output conversion** — when result is `xr.DataArray` and first arg was:
| Original type | Output type |
|---|---|
| `list` | `list` via `.values.tolist()` |
| `np.ndarray` | `np.ndarray` via `.values` |
| `torch.Tensor` | `torch.Tensor` |
| `pd.DataFrame` | `pd.DataFrame(result.values)` |
| `pd.Series` | `pd.Series(result.values.flatten())` |

---

### `signal_fn`

```python
from scitex.decorators import signal_fn

@signal_fn
def bandpass(signal, fs, low_hz, high_hz):
    # Only `signal` (first arg) is converted to torch.Tensor.
    # fs, low_hz, high_hz remain as Python scalars.
    ...
    return filtered  # torch.Tensor or tuple of tensors
```

**Signature:** `signal_fn(func: Callable) -> Callable`

`signal_fn` is a variant of `torch_fn` designed for DSP functions where:
- Only **the first argument** (the signal array) is converted to `torch.Tensor`.
- All remaining arguments (`fs`, `bands`, threshold values, etc.) are passed through **unchanged** as Python scalars or lists.

**Output conversion** — supports both single-tensor and tuple returns:
- Single `torch.Tensor` — converted back to caller's original type.
- `tuple` — each tensor element is converted back individually; non-tensor elements pass through.

---

## Converter Utilities

Standalone helpers from `scitex.decorators._converters` (also exported from `stx.decorators`):

```python
from scitex.decorators import to_numpy, to_torch, is_torch, is_cuda, ConversionWarning

# Check types
is_torch(arr)          # True if any arg is torch.Tensor
is_cuda(arr)           # True if any arg is a CUDA tensor

# Convert data
arr_np = to_numpy(tensor)    # returns np.ndarray
arr_t = to_torch(arr)        # returns torch.Tensor (auto-device)
```

`to_torch` signature:
```python
to_torch(*args, return_fn=_return_if, device=None, **kwargs)
```
- `device` defaults to `"cuda"` if available, else `"cpu"`.
- `axis` kwargs are renamed to `dim` automatically.

`to_numpy` signature:
```python
to_numpy(*args, return_fn=_return_if, **kwargs)
```
- `dim` kwargs are renamed to `axis` automatically.

`is_nested_decorator()` — inspects the call stack for nested `wrapper` frames with `_current_decorator` locals to detect multi-decorator stacking and prevent double-conversion.
