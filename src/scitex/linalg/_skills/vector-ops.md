---
name: linalg-vector-ops
description: Vector operations — cosine similarity (NaN-safe), NaN-aware norm, vector projection/rebasing, and coordinate reconstruction from three line lengths.
---

# Vector Operations

## cosine

Computes the cosine similarity between two 1-D vectors. Returns `np.nan` if either input contains any NaN value.

```python
cosine(v1, v2) -> float
```

**Parameters**

| Parameter | Type | Description |
|-----------|------|-------------|
| `v1` | array_like (1-D) | First vector |
| `v2` | array_like (1-D) | Second vector |

**Return value**: scalar in `[-1, 1]`, or `np.nan` if any element of `v1` or `v2` is NaN.

Uses `scipy.linalg.norm` for the denominator.

**Examples**

```python
import scitex as stx
import numpy as np

stx.linalg.cosine(np.array([1, 0]), np.array([0, 1]))   # 0.0  (orthogonal)
stx.linalg.cosine(np.array([1, 0]), np.array([1, 0]))   # 1.0  (identical)
stx.linalg.cosine(np.array([1, 0]), np.array([-1, 0]))  # -1.0 (opposite)

# NaN propagation
v_nan = np.array([np.nan, 1.0])
stx.linalg.cosine(v_nan, np.array([1, 0]))              # np.nan
```

---

## nannorm

Computes the vector norm along a given axis. Returns `np.nan` if the input contains any NaN value (rather than computing a misleading partial norm).

```python
nannorm(v, axis=-1) -> float or np.nan
```

**Parameters**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `v` | array_like | required | Input vector or array |
| `axis` | int | `-1` | Axis along which the norm is computed |

Uses `scipy.linalg.norm`.

**Examples**

```python
import scitex as stx
import numpy as np

stx.linalg.nannorm(np.array([3.0, 4.0]))          # 5.0
stx.linalg.nannorm(np.array([np.nan, 4.0]))        # np.nan

# 2-D array — norm of each row (axis=-1 default)
A = np.array([[3.0, 4.0], [0.0, 1.0]])
stx.linalg.nannorm(A)                              # array([5., 1.])
```

---

## rebase_a_vec

Projects vector `v` onto the direction of `v_base` and returns the signed scalar length of that projection. Equivalent to asking: "how far along `v_base` does `v` reach?"

Returns `np.nan` if either `v` or `v_base` contains any NaN value.

```python
rebase_a_vec(v, v_base) -> float or np.nan
```

**Parameters**

| Parameter | Type | Description |
|-----------|------|-------------|
| `v` | array_like (1-D) | Vector to project |
| `v_base` | array_like (1-D) | Reference (base) direction vector |

**Return value**: signed scalar. Positive when `v` and `v_base` point in the same general direction (`cosine > 0`), negative when opposite.

**How it works**

1. Computes the production vector: `‖v‖ · cos(v, v_base) · v_base / ‖v_base‖`
2. Takes the sign from `cosine(v, v_base)` to preserve direction.
3. Returns `sign · ‖production_vector‖`.

**Examples**

```python
import scitex as stx
import numpy as np

v      = np.array([3.0, 4.0])
v_base = np.array([10.0, 0.0])   # x-axis direction

# Project v onto the x-axis: only the x-component (3.0) counts
stx.linalg.rebase_a_vec(v, v_base)          # 3.0

# Opposite direction
v_opp = np.array([-3.0, 4.0])
stx.linalg.rebase_a_vec(v_opp, v_base)      # -3.0

# NaN propagation
stx.linalg.rebase_a_vec(np.array([np.nan, 1.0]), v_base)  # np.nan
```

---

## three_line_lengths_to_coords

Given three line lengths `aa`, `bb`, `cc` forming a triangle (where `aa` = OA, `bb` = OB, `cc` = AB), reconstructs the 3-D Cartesian coordinates of the three vertices O, A, B. The triangle is placed flat in the xy-plane (z=0), with O at the origin and A on the x-axis.

```python
three_line_lengths_to_coords(aa, bb, cc) -> tuple[tuple, tuple, tuple]
```

**Parameters**

| Parameter | Type | Description |
|-----------|------|-------------|
| `aa` | float | Length of side OA |
| `bb` | float | Length of side OB |
| `cc` | float | Length of side AB |

**Returns**: `(O, A, B)` where each element is a 3-tuple `(x, y, z)`.

- `O = (0, 0, 0)` — origin, always
- `A = (aa, 0, 0)` — on the positive x-axis
- `B = (b1, b2, 0)` — computed via law of cosines; `b2` is a `sympy` symbolic result cast to float

Uses `sympy.solve` internally for the y-coordinate of B.

**Examples**

```python
import scitex as stx
import numpy as np

# Right triangle: OA=2, OB=√3, AB=1
O, A, B = stx.linalg.three_line_lengths_to_coords(2, np.sqrt(3), 1)
# O = (0, 0, 0)
# A = (2, 0, 0)
# B ≈ (1.5, 0.866, 0)   — 30-60-90 triangle

# Equilateral triangle with side length 1
O, A, B = stx.linalg.three_line_lengths_to_coords(1, 1, 1)
# O = (0,   0,    0)
# A = (1,   0,    0)
# B ≈ (0.5, 0.866, 0)
```

**Note**: inputs must satisfy the triangle inequality (`aa + bb > cc`, etc.). No validation is performed; invalid inputs will produce imaginary coordinates or a `sympy` error.
