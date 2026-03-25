---
name: stx.cv.io
description: Image I/O and color space conversion — load, save, to_rgb, to_bgr, to_gray.
---

# stx.cv — Image I/O

Source file: `src/scitex/cv/_io.py`

## load

```python
stx.cv.load(
    path: str | Path,
    color: bool = True,
    alpha: bool = False,
) -> np.ndarray
```

Load an image from file using `cv2.imread`.

- `color=True` (default): returns a BGR array.
- `color=False`: returns a single-channel grayscale array.
- `alpha=True`: preserves the alpha channel (BGRA, 4 channels).
- Raises `FileNotFoundError` if `cv2.imread` returns `None`.

```python
import scitex.cv as cv

img  = cv.load("photo.png")            # BGR, HxWx3
gray = cv.load("photo.png", color=False)  # grayscale, HxW
rgba = cv.load("photo.png", alpha=True)   # BGRA, HxWx4
```

## save

```python
stx.cv.save(
    img: np.ndarray,
    path: str | Path,
    quality: int = 95,
) -> Path
```

Save an image to file. Parent directories are created automatically.

- JPEG: `quality` maps directly to `cv2.IMWRITE_JPEG_QUALITY` (0–100).
- PNG: `quality` is mapped to `cv2.IMWRITE_PNG_COMPRESSION` via `(100 - quality) // 10`, clamped to 0–9.
- All other extensions: no extra params passed.
- Raises `OSError` if `cv2.imwrite` returns `False`.
- Returns the `Path` of the saved file.

```python
cv.save(img, "output.jpg")           # quality=95
cv.save(img, "output.jpg", quality=80)
cv.save(img, "output.png", quality=90)
cv.save(img, "subdir/output.bmp")    # subdir is created
```

## to_rgb

```python
stx.cv.to_rgb(img: np.ndarray) -> np.ndarray
```

Convert to RGB. Handles three input types automatically:

| Input shape | Input format | Conversion |
|---|---|---|
| `(H, W)` | Grayscale | `COLOR_GRAY2RGB` |
| `(H, W, 4)` | BGRA | `COLOR_BGRA2RGB` |
| `(H, W, 3)` | BGR | `COLOR_BGR2RGB` |

```python
rgb = cv.to_rgb(bgr_img)
```

## to_bgr

```python
stx.cv.to_bgr(img: np.ndarray) -> np.ndarray
```

Convert to BGR. Handles three input types automatically:

| Input shape | Input format | Conversion |
|---|---|---|
| `(H, W)` | Grayscale | `COLOR_GRAY2BGR` |
| `(H, W, 4)` | RGBA | `COLOR_RGBA2BGR` |
| `(H, W, 3)` | RGB | `COLOR_RGB2BGR` |

```python
bgr = cv.to_bgr(rgb_img)
```

## to_gray

```python
stx.cv.to_gray(img: np.ndarray) -> np.ndarray
```

Convert to single-channel grayscale. If input is already 2D (grayscale) it is returned unchanged.

| Input shape | Conversion |
|---|---|
| `(H, W)` | Identity (returned as-is) |
| `(H, W, 4)` | `COLOR_BGRA2GRAY` |
| `(H, W, 3)` | `COLOR_BGR2GRAY` |

```python
gray = cv.to_gray(img)
```

## Typical Workflow

```python
import scitex.cv as cv

img  = cv.load("input.png")          # BGR ndarray
rgb  = cv.to_rgb(img)                # for matplotlib
gray = cv.to_gray(img)               # grayscale
cv.save(gray, "gray_out.png")
```
