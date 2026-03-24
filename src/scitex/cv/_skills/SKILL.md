---
name: stx.cv
description: Computer vision utilities for image I/O, transforms, filters, and drawing via OpenCV.
---

# stx.cv

The `stx.cv` module provides reusable OpenCV-based utilities for image processing. It covers image loading/saving, geometric transforms, image filters, and drawing primitives.

## Python API

```python
import scitex.cv as cv

# I/O and color conversion
img = cv.load("input.png")               # Load as numpy array (RGB)
cv.save(img, "output.png")
gray = cv.to_gray(img)
bgr = cv.to_bgr(img)

# Transforms
img = cv.resize(img, scale=0.5)
img = cv.rotate(img, angle=90)
img = cv.flip(img, axis="horizontal")
img = cv.crop(img, x=10, y=10, w=200, h=200)
img = cv.pad(img, padding=20, color=(0, 0, 0))

# Filters
img = cv.blur(img, ksize=5)
img = cv.sharpen(img)
edges = cv.edge_detect(img, method="canny")
binary = cv.threshold(img, thresh=127)
img = cv.denoise(img)

# Drawing
cv.rectangle(img, (10, 10), (100, 100), color=(255, 0, 0))
cv.circle(img, center=(50, 50), radius=20)
cv.text(img, "Label", position=(10, 30))
cv.line(img, (0, 0), (100, 100))
```

## Key Features

- `load` / `save` — image I/O with automatic format detection
- `to_rgb` / `to_bgr` / `to_gray` — color space conversions
- Transform: `resize`, `rotate`, `flip`, `crop`, `pad`
- Filters: `blur`, `sharpen`, `edge_detect`, `threshold`, `denoise`
- Drawing: `rectangle`, `circle`, `line`, `text`, `polylines`, `arrow`
