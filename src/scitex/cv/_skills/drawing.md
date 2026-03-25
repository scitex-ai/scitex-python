---
name: stx.cv.drawing
description: Drawing primitives on images — rectangle, circle, line, text, polylines, arrow.
---

# stx.cv — Drawing

Source file: `src/scitex/cv/_draw.py`

All drawing functions **modify the image in place** via OpenCV and **also return it**, enabling chaining.

Colors are specified as `(B, G, R)` tuples (OpenCV BGR order).

## rectangle

```python
stx.cv.rectangle(
    img: np.ndarray,
    pt1: tuple[int, int],
    pt2: tuple[int, int],
    color: tuple[int, int, int] = (0, 255, 0),
    thickness: int = 2,
    filled: bool = False,
) -> np.ndarray
```

Draw a rectangle from `pt1` (top-left) to `pt2` (bottom-right).

- `filled=True` passes `thickness=-1` to `cv2.rectangle`.

```python
import scitex.cv as cv

cv.rectangle(img, (10, 10), (100, 80))                        # green outline
cv.rectangle(img, (10, 10), (100, 80), color=(0, 0, 255))     # red outline
cv.rectangle(img, (10, 10), (100, 80), filled=True)           # filled green
```

## circle

```python
stx.cv.circle(
    img: np.ndarray,
    center: tuple[int, int],
    radius: int,
    color: tuple[int, int, int] = (0, 255, 0),
    thickness: int = 2,
    filled: bool = False,
) -> np.ndarray
```

Draw a circle.

- `filled=True` passes `thickness=-1` to `cv2.circle`.

```python
cv.circle(img, center=(50, 50), radius=20)
cv.circle(img, center=(50, 50), radius=20, filled=True, color=(255, 0, 0))
```

## line

```python
stx.cv.line(
    img: np.ndarray,
    pt1: tuple[int, int],
    pt2: tuple[int, int],
    color: tuple[int, int, int] = (0, 255, 0),
    thickness: int = 2,
) -> np.ndarray
```

Draw a straight line from `pt1` to `pt2`.

```python
cv.line(img, (0, 0), (200, 200))
cv.line(img, (0, 0), (200, 200), color=(255, 255, 0), thickness=4)
```

## text

```python
stx.cv.text(
    img: np.ndarray,
    text: str,
    position: tuple[int, int],
    color: tuple[int, int, int] = (255, 255, 255),
    scale: float = 1.0,
    thickness: int = 2,
    font: str = "simplex",
) -> np.ndarray
```

Draw a text string. `position` is the **bottom-left** corner of the text baseline.

| `font` | cv2 constant |
|---|---|
| `'simplex'` | `FONT_HERSHEY_SIMPLEX` |
| `'plain'` | `FONT_HERSHEY_PLAIN` |
| `'duplex'` | `FONT_HERSHEY_DUPLEX` |
| `'complex'` | `FONT_HERSHEY_COMPLEX` |
| `'triplex'` | `FONT_HERSHEY_TRIPLEX` |

```python
cv.text(img, "Hello", position=(10, 30))
cv.text(img, "Score: 0.95", position=(10, 60), scale=0.8, color=(0, 255, 255))
cv.text(img, "Label", position=(20, 50), font="duplex", thickness=1)
```

## polylines

```python
stx.cv.polylines(
    img: np.ndarray,
    points: np.ndarray,
    closed: bool = True,
    color: tuple[int, int, int] = (0, 255, 0),
    thickness: int = 2,
) -> np.ndarray
```

Draw connected line segments through a sequence of points.

- `points`: shape `(N, 2)` or `(N, 1, 2)`; converted to `int32` internally.
- `closed=True`: connects the last point back to the first (polygon).

```python
import numpy as np

pts = np.array([[10, 10], [50, 5], [90, 10], [50, 60]], dtype=np.int32)
cv.polylines(img, pts)                          # closed polygon
cv.polylines(img, pts, closed=False)            # open path
cv.polylines(img, pts, color=(0, 0, 255), thickness=3)
```

## arrow

```python
stx.cv.arrow(
    img: np.ndarray,
    pt1: tuple[int, int],
    pt2: tuple[int, int],
    color: tuple[int, int, int] = (0, 255, 0),
    thickness: int = 2,
    tip_length: float = 0.1,
) -> np.ndarray
```

Draw an arrowed line. The arrowhead is at `pt2`.

- `tip_length`: arrow tip length as a fraction of the total line length (passed to `cv2.arrowedLine`).

```python
cv.arrow(img, (10, 50), (200, 50))                           # pointing right
cv.arrow(img, (10, 50), (200, 50), tip_length=0.2)           # larger arrowhead
cv.arrow(img, (100, 10), (100, 150), color=(0, 0, 255))      # pointing down
```

## Chaining Example

```python
import scitex.cv as cv

img = cv.load("frame.png")
(
    cv.rectangle(img, (10, 10), (200, 200), color=(0, 0, 255))
    and cv.text(img, "Object", (12, 30), color=(0, 0, 255))
    and cv.circle(img, (105, 105), 5, filled=True)
)
cv.save(img, "annotated.png")
```
