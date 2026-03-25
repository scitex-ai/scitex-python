---
name: stx.cv.transforms
description: Geometric image transformations — resize, rotate, flip, crop, pad.
---

# stx.cv — Image Transforms

Source file: `src/scitex/cv/_transform.py`

## resize

```python
stx.cv.resize(
    img: np.ndarray,
    size: tuple[int, int] | None = None,
    scale: float | None = None,
    interpolation: str = "linear",
) -> np.ndarray
```

Resize an image. Exactly one of `size` or `scale` must be provided; providing neither raises `ValueError`.

- `size`: target `(width, height)` tuple passed directly to `cv2.resize`.
- `scale`: uniform scale factor applied to both dimensions.
- `interpolation` options: `'nearest'`, `'linear'` (default), `'cubic'`, `'area'`, `'lanczos'`.

```python
import scitex.cv as cv

half    = cv.resize(img, scale=0.5)
big     = cv.resize(img, size=(1920, 1080))
precise = cv.resize(img, scale=2.0, interpolation="lanczos")
thumb   = cv.resize(img, scale=0.25, interpolation="area")  # best for downscale
```

## rotate

```python
stx.cv.rotate(
    img: np.ndarray,
    angle: float,
    center: tuple[int, int] | None = None,
    scale: float = 1.0,
) -> np.ndarray
```

Rotate an image using an affine warp.

- `angle`: counter-clockwise degrees.
- `center`: rotation pivot `(x, y)`. Defaults to image center `(w//2, h//2)`.
- `scale`: simultaneous zoom factor.
- Output size equals input size; content outside is filled with black.

```python
rot90 = cv.rotate(img, 90)
rot45 = cv.rotate(img, 45)
zoomed = cv.rotate(img, 0, scale=1.2)
custom = cv.rotate(img, 30, center=(100, 100))
```

## flip

```python
stx.cv.flip(
    img: np.ndarray,
    direction: str = "horizontal",
) -> np.ndarray
```

Flip an image along an axis.

| `direction` | cv2 flip code | Effect |
|---|---|---|
| `'horizontal'` | `1` | Mirror left-right |
| `'vertical'` | `0` | Mirror top-bottom |
| `'both'` | `-1` | 180-degree rotation |

```python
mirrored = cv.flip(img, "horizontal")
updown   = cv.flip(img, "vertical")
rotated  = cv.flip(img, "both")
```

## crop

```python
stx.cv.crop(
    img: np.ndarray,
    x: int,
    y: int,
    width: int,
    height: int,
) -> np.ndarray
```

Crop a rectangular region from an image.

- `x, y`: top-left corner in pixel coordinates.
- `width, height`: crop dimensions.
- Returns a copy of the slice `img[y:y+height, x:x+width]`.

```python
face = cv.crop(img, x=50, y=30, width=200, height=200)
```

## pad

```python
stx.cv.pad(
    img: np.ndarray,
    top: int = 0,
    bottom: int = 0,
    left: int = 0,
    right: int = 0,
    color: int | tuple = 0,
    mode: str = "constant",
) -> np.ndarray
```

Add border padding to an image.

| `mode` | cv2 border type | Description |
|---|---|---|
| `'constant'` | `BORDER_CONSTANT` | Solid color fill (uses `color`) |
| `'reflect'` | `BORDER_REFLECT` | Mirror reflection at edges |
| `'replicate'` | `BORDER_REPLICATE` | Extend edge pixels |

```python
# 20px black border on all sides
padded = cv.pad(img, top=20, bottom=20, left=20, right=20)

# Letterbox: add white bars top/bottom
letter = cv.pad(img, top=50, bottom=50, color=(255, 255, 255))

# Reflective padding
reflected = cv.pad(img, top=10, left=10, mode="reflect")
```
