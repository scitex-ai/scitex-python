---
description: Get a one-shot snapshot of CPU/RAM/GPU/VRAM usage or log it over time to a CSV file.
---

# stx.resource — Processor Usage Monitoring

## get_processor_usages

Returns a one-row `pd.DataFrame` with current CPU, RAM, GPU, and VRAM readings.

```python
from scitex.resource import get_processor_usages

df = get_processor_usages()
print(df)
#              Timestamp  CPU [%]  RAM [GiB]  GPU [%]  VRAM [GiB]
# 0  2024-11-04 10:30:15     25.3        8.2     65.0         4.5
```

Columns:
- `Timestamp` — `datetime` of the sample
- `CPU [%]` — system-wide CPU utilization via `psutil.cpu_percent()`
- `RAM [GiB]` — RAM used in GiB (percent × total)
- `GPU [%]` — GPU utilization from `nvidia-smi`; `0.0` if unavailable
- `VRAM [GiB]` — VRAM used in GiB from `nvidia-smi`; `0.0` if unavailable

GPU values fall back to `0.0` silently when `nvidia-smi` is not present.

## log_processor_usages

Polls `get_processor_usages()` at a fixed interval and appends each row to a CSV file.

```python
from scitex.resource import log_processor_usages

# Foreground: blocks for 30 minutes, sampling every 1 s
log_processor_usages(
    path="/tmp/scitex/processor_usages.csv",
    limit_min=30,
    interval_s=1,
    init=True,      # True: clear existing file before starting
    verbose=False,
)

# Background: returns a multiprocessing.Process
proc = log_processor_usages(
    path="/tmp/resource_log.csv",
    limit_min=60,
    interval_s=5,
    background=True,
)
proc.terminate()  # Stop early

# Monitor live with tail (printed to console at start)
# tail -f /tmp/scitex/processor_usages.csv
```

The CSV is written in append mode without loading the whole file, keeping memory usage flat.

`main` is an alias for `log_processor_usages` (used by `python -m scitex.resource`).
