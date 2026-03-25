---
name: stx.cv.filters
description: Image filtering — blur, sharpen, edge_detect, threshold, denoise.
---

# stx.cv — Image Filters

Source file: `src/scitex/cv/_filters.py`

## blur

```python
stx.cv.blur(
    img: np.ndarray,
    ksize: int = 5,
    method: str = "gaussian",
) -> np.ndarray
```

Apply a blurring filter. If `ksize` is even it is incremented to the next odd number automatically.

| `method` | cv2 call | Notes |
|---|---|---|
| `'gaussian'` | `cv2.GaussianBlur` | Smooth; sigmaX computed automatically |
| `'median'` | `cv2.medianBlur` | Good for salt-and-pepper noise |
| `'box'` | `cv2.blur` | Simple averaging |
| `'bilateral'` | `cv2.bilateralFilter` | Edge-preserving; sigmaColor/sigmaSpace = 75 |

```python
import scitex.cv as cv

smooth  = cv.blur(img)                        # gaussian, ksize=5
median  = cv.blur(img, ksize=7, method="median")
edge_pres = cv.blur(img, ksize=9, method="bilateral")
```

## sharpen

```python
stx.cv.sharpen(
    img: np.ndarray,
    strength: float = 1.0,
) -> np.ndarray
```

Sharpen using a Laplacian-based unsharp kernel via `cv2.filter2D`.

- Base kernel: `[[0,-1,0],[-1,5,-1],[0,-1,0]]` (identity + edge enhancement).
- When `strength != 1.0`: kernel is interpolated as `I + strength * (K - I)` where `I` is the 3x3 identity.

```python
sharp = cv.sharpen(img)
more  = cv.sharpen(img, strength=2.0)
less  = cv.sharpen(img, strength=0.5)
```

## edge_detect

```python
stx.cv.edge_detect(
    img: np.ndarray,
    method: str = "canny",
    low: int = 50,
    high: int = 150,
) -> np.ndarray
```

Detect edges. Color images are converted to grayscale internally before detection.

| `method` | Algorithm | Output dtype |
|---|---|---|
| `'canny'` | Canny (uses `low`/`high` thresholds) | `uint8` binary mask |
| `'sobel'` | Sobel X + Y combined as magnitude | `uint8` |
| `'laplacian'` | Laplacian of Gaussian | `uint8` (absolute value) |

- `low`, `high` only affect the `'canny'` method.

```python
edges   = cv.edge_detect(img)                     # Canny, default thresholds
edges   = cv.edge_detect(img, low=30, high=100)   # Canny, custom thresholds
sobel   = cv.edge_detect(img, method="sobel")
laplace = cv.edge_detect(img, method="laplacian")
```

## threshold

```python
stx.cv.threshold(
    img: np.ndarray,
    thresh: int = 127,
    maxval: int = 255,
    method: str = "binary",
) -> np.ndarray
```

Binarize or clip an image. Color images are converted to grayscale internally.

| `method` | Notes |
|---|---|
| `'binary'` | Pixels above `thresh` → `maxval`, else 0 |
| `'binary_inv'` | Inverse of binary |
| `'trunc'` | Pixels above `thresh` set to `thresh` |
| `'tozero'` | Pixels below `thresh` set to 0 |
| `'tozero_inv'` | Pixels above `thresh` set to 0 |
| `'otsu'` | Otsu's automatic threshold (`thresh` ignored); uses `cv2.THRESH_OTSU` |
| `'adaptive_mean'` | Adaptive mean threshold; block size=11, C=2 |
| `'adaptive_gaussian'` | Adaptive Gaussian threshold; block size=11, C=2 |

```python
binary   = cv.threshold(img)                          # binary, thresh=127
otsu     = cv.threshold(img, method="otsu")           # automatic threshold
adaptive = cv.threshold(img, method="adaptive_gaussian")
inv      = cv.threshold(img, thresh=100, method="binary_inv")
```

## denoise

```python
stx.cv.denoise(
    img: np.ndarray,
    strength: int = 10,
    method: str = "fastNl",
) -> np.ndarray
```

Remove noise from an image.

| `method` | Color images | Grayscale |
|---|---|---|
| `'fastNl'` | `cv2.fastNlMeansDenoisingColored(img, None, strength, strength)` | `cv2.fastNlMeansDenoising(img, None, strength)` |
| `'bilateral'` | `cv2.bilateralFilter(img, 9, strength*7.5, strength*7.5)` | Same |

- `'fastNl'` (Non-Local Means) is the default and generally higher quality.
- `'bilateral'` is faster but edge-preserving only.

```python
clean = cv.denoise(img)                        # fastNl, strength=10
light = cv.denoise(img, strength=5)            # milder
fast  = cv.denoise(img, method="bilateral")
```
