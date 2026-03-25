---
name: gen-timestamper
description: TimeStamper class in stx.gen — records elapsed time with comments, returns formatted strings, and stores a pandas DataFrame of all checkpoint events. Useful for profiling multi-stage pipelines.
---

# TimeStamper

A callable class that measures elapsed time from object creation and between successive calls. Each call records a labeled checkpoint and returns a formatted string. All records are accessible as a `pandas.DataFrame`.

```python
from scitex.gen import TimeStamper
```

---

## Constructor

```python
TimeStamper(is_simple: bool = True) -> TimeStamper
```

| Parameter | Default | Description |
|-----------|---------|-------------|
| `is_simple` | `True` | `True`: compact format `"ID:0 | 00:00:01 label |"`. `False`: verbose format with both total and delta times. |

---

## Calling the stamper

```python
ts(comment: str = "", verbose: bool = False) -> str
```

Returns a formatted timestamp string and records the checkpoint internally.

| Parameter | Default | Description |
|-----------|---------|-------------|
| `comment` | `""` | Label for this checkpoint |
| `verbose` | `False` | If `True`, also prints the string to stdout |

**Simple format** (`is_simple=True`):
```
"ID:0 | 00:00:01 Starting process | "
```

**Verbose format** (`is_simple=False`):
```
"Time (id:0): total 00:00:01, prev 00:00:01 [hh:mm:ss]: Starting process\n"
```

---

## record property

```python
ts.record -> pd.DataFrame
```

Returns a DataFrame with columns: `timestamp`, `elapsed_since_start`, `elapsed_since_prev`, `comment`. The `formatted_text` column is excluded.

---

## delta method

```python
ts.delta(id1: int, id2: int) -> float
```

Returns the difference in seconds between two checkpoint timestamps. Supports negative indices (Python-style).

| Parameter | Description |
|-----------|-------------|
| `id1` | First checkpoint ID |
| `id2` | Second checkpoint ID |

Raises `ValueError` if either ID does not exist.

---

## Full example

```python
import time
import scitex as stx

ts = stx.gen.TimeStamper(is_simple=True)

ts("Loading data", verbose=True)
# ID:0 | 00:00:00 Loading data |

time.sleep(1)
ts("Preprocessing", verbose=True)
# ID:1 | 00:00:01 Preprocessing |

time.sleep(2)
ts("Training", verbose=True)
# ID:2 | 00:00:03 Training |

# DataFrame of all checkpoints
print(ts.record)
#    timestamp  elapsed_since_start  elapsed_since_prev       comment
# 0  ...        0.000                0.000               Loading data
# 1  ...        1.002                1.002               Preprocessing
# 2  ...        3.004                2.002               Training

# Time between step 1 and step 0 (positive = id1 is later)
diff = ts.delta(1, 0)
# ≈ 1.002

# Negative index: last minus first
diff = ts.delta(-1, 0)
# ≈ 3.004
```

---

## Profiling pipelines

```python
ts = stx.gen.TimeStamper(is_simple=False)

for i, batch in enumerate(dataloader):
    ts(f"batch {i} loaded")
    result = model(batch)
    ts(f"batch {i} forward")

# All timings in one DataFrame
print(ts.record[["elapsed_since_prev", "comment"]])
```
