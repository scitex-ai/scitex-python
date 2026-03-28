---
name: stx.cv
description: Computer vision utilities — image I/O, geometric transforms, filters, and drawing primitives via OpenCV. Use when loading/saving images or applying cv2-based processing in the SciTeX ecosystem.
user-invocable: false
---

# stx.cv — Computer Vision

OpenCV-based image processing utilities. Import with:

```python
import scitex.cv as cv
# or
import scitex as stx; stx.cv.<function>
```

## Sub-skills

### I/O and Color Conversion
- [io.md](io.md) — `load`, `save`, `to_rgb`, `to_bgr`, `to_gray`: file loading/saving with format-aware quality params, and color space conversions that handle grayscale/BGR/BGRA automatically.

### Geometric Transforms
- [transforms.md](transforms.md) — `resize`, `rotate`, `flip`, `crop`, `pad`: scale by factor or target size, rotate around arbitrary center, flip on any axis, crop rectangles, pad with constant/reflect/replicate borders.

### Image Filters
- [filters.md](filters.md) — `blur`, `sharpen`, `edge_detect`, `threshold`, `denoise`: four blur methods, unsharp masking, three edge detectors (Canny/Sobel/Laplacian), eight threshold strategies including Otsu and adaptive, and two denoising methods.

### Drawing Primitives
- [drawing.md](drawing.md) — `rectangle`, `circle`, `line`, `text`, `polylines`, `arrow`: annotate images in place with shapes and labels; all functions return the modified image for chaining.

## Quick Reference

```python
import scitex.cv as cv

# I/O
img  = cv.load("input.png")            # BGR ndarray
cv.save(img, "output.jpg", quality=90)
rgb  = cv.to_rgb(img)                  # for matplotlib
gray = cv.to_gray(img)

# Transforms
img = cv.resize(img, scale=0.5)
img = cv.resize(img, size=(640, 480), interpolation="lanczos")
img = cv.rotate(img, angle=90)
img = cv.flip(img, direction="horizontal")
img = cv.crop(img, x=10, y=10, width=200, height=200)
img = cv.pad(img, top=20, bottom=20, left=20, right=20, color=0)

# Filters
img   = cv.blur(img, ksize=5, method="gaussian")
img   = cv.sharpen(img, strength=1.5)
edges = cv.edge_detect(img, method="canny", low=50, high=150)
mask  = cv.threshold(img, method="otsu")
img   = cv.denoise(img, strength=10)

# Drawing (modify in place, return img)
cv.rectangle(img, (10, 10), (100, 80), color=(0, 255, 0))
cv.circle(img, center=(50, 50), radius=20, filled=True)
cv.line(img, (0, 0), (200, 200))
cv.text(img, "Label", position=(10, 30), scale=0.8)
cv.arrow(img, (10, 50), (150, 50), tip_length=0.15)
```
