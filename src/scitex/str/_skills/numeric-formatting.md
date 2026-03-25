---
description: Factor out common powers of 10 from axis tick values for cleaner scientific notation, auto-apply to matplotlib axes, and convert byte counts to human-readable strings.
---

# Numeric Formatting

---

## factor_out_digits

Factor out the common order of magnitude from a set of numerical values and return both the scaled values and a display string (e.g. `$\times 10^{3}$`).

```python
factor_out_digits(
    values: Union[List, np.ndarray, float, int],
    precision: int = 2,
    min_factor_power: int = 3,
    return_latex: bool = True,
    return_unicode: bool = False,
) -> Tuple[Union[List, np.ndarray, float], str]
```

**Parameters**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `values` | list / ndarray / scalar | required | Numerical values to factor |
| `precision` | `int` | `2` | Decimal places for the factored values |
| `min_factor_power` | `int` | `3` | Minimum `|power|` to trigger factoring; powers below this are left as-is |
| `return_latex` | `bool` | `True` | Format factor string as `$\times 10^{n}$` |
| `return_unicode` | `bool` | `False` | Format factor string with Unicode superscripts (`×10³`) |

**Returns** `(factored_values, factor_string)` where `factor_string` is `""` when no factoring occurs.

**Algorithm**

1. Remove zeros, compute log₁₀ of absolute values.
2. `common_power = floor(mean(log₁₀(|values|)))`.
3. If `|common_power| < min_factor_power`, return original unchanged.
4. Divide all values by `10^common_power`, round to `precision`.

**Examples**

```python
import scitex as stx

stx.str.factor_out_digits([1000, 2000, 3000])
# ([1.0, 2.0, 3.0], '$\\times 10^{3}$')

stx.str.factor_out_digits([0.001, 0.002, 0.003])
# ([1.0, 2.0, 3.0], '$\\times 10^{-3}$')

stx.str.factor_out_digits([1.5e6, 2.3e6, 4.1e6])
# ([1.5, 2.3, 4.1], '$\\times 10^{6}$')

# Unicode superscripts
stx.str.factor_out_digits([5000, 6000], return_latex=False, return_unicode=True)
# ([5.0, 6.0], '×10³')

# Small power — no factoring
stx.str.factor_out_digits([100, 200], min_factor_power=3)
# ([100, 200], '')
```

---

## auto_factor_axis

Apply `factor_out_digits` directly to a matplotlib axes object, updating tick labels in place and adding a factor annotation.

```python
auto_factor_axis(
    ax,
    axis: str = "both",
    precision: int = 2,
    min_factor_power: int = 3,
    return_latex: bool = True,
    return_unicode: bool = False,
    label_offset: Tuple[float, float] = (0.02, 0.98),
) -> None
```

**Parameters**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `ax` | `matplotlib.axes.Axes` | required | Axes to modify |
| `axis` | `str` | `"both"` | Which axis: `"x"`, `"y"`, or `"both"` |
| `label_offset` | `(float, float)` | `(0.02, 0.98)` | Axes-coordinate position for the factor text annotation |
| remaining | — | same as `factor_out_digits` | Passed through |

**Behavior**

- For each factored axis: replaces tick labels with scaled values, adds a small text box (white background, rounded corners) showing the factor string.
- X-axis annotation placed at `(label_offset[0], 0.02)`.
- Y-axis annotation placed at `(0.02, label_offset[1])`.
- No-op when `factor_string` is empty (power below threshold).

**Example**

```python
import matplotlib.pyplot as plt
import scitex as stx

fig, ax = plt.subplots()
ax.plot([1000, 2000, 3000], [0.001, 0.002, 0.003])
stx.str.auto_factor_axis(ax, axis="both")
# x-axis ticks become 1.0, 2.0, 3.0 with "×10³" annotation
# y-axis ticks become 1.0, 2.0, 3.0 with "×10⁻³" annotation
```

---

## smart_tick_formatter

Combine nice tick selection (via `matplotlib.ticker.MaxNLocator`) with `factor_out_digits`.

```python
smart_tick_formatter(
    values: Union[List, np.ndarray],
    max_ticks: int = 6,
    factor_out: bool = True,
    precision: int = 2,
    min_factor_power: int = 3,
    return_latex: bool = True,
) -> Tuple[np.ndarray, List[str], str]
```

**Parameters**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `values` | list / ndarray | required | Data values to derive ticks from |
| `max_ticks` | `int` | `6` | Maximum number of ticks |
| `factor_out` | `bool` | `True` | Apply factoring; set `False` to get plain labels |
| remaining | — | same as `factor_out_digits` | Passed through |

**Returns** `(tick_positions, tick_labels, factor_string)`

- `tick_positions`: array from `MaxNLocator`
- `tick_labels`: list of string labels (trailing zeros stripped)
- `factor_string`: e.g. `'$\\times 10^{3}$'` or `""` when unused

**Example**

```python
import scitex as stx

positions, labels, factor = stx.str.smart_tick_formatter([1000, 1500, 2000, 2500, 3000])
# positions: array([1000., 1200., 1400., 1600., 1800., 2000., 2200., ...])
# labels:    ['1', '1.2', '1.4', ...]
# factor:    '$\\times 10^{3}$'
```

---

## readable_bytes

Convert a byte count to a human-readable IEC binary string.

```python
readable_bytes(num: int, suffix: str = "B") -> str
```

**Parameters**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `num` | `int` | required | Number of bytes |
| `suffix` | `str` | `"B"` | Unit suffix appended after the prefix |

**Scale** — divides by 1024 at each step through: (none) Ki Mi Gi Ti Pi Ei Zi Yi

**Examples**

```python
import scitex as stx

stx.str.readable_bytes(1024)
# '1.0 KiB'

stx.str.readable_bytes(1048576)
# '1.0 MiB'

stx.str.readable_bytes(1073741824)
# '1.0 GiB'

stx.str.readable_bytes(1500)
# '1.5 KiB'

# Custom suffix
stx.str.readable_bytes(2048, suffix="ytes")
# '2.0 Kiytes'
```
