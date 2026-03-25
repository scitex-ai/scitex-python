---
name: resource-monitoring
description: Sample instantaneous CPU/GPU/memory usage with get_processor_usages() and log usage over time to a CSV file with log_processor_usages().
---

# Usage Monitoring

## get_processor_usages

Return a dict of current CPU, GPU, and memory utilization percentages.

```python
get_processor_usages() -> dict
```

```python
import scitex as stx

usage = stx.resource.get_processor_usages()
print(usage)
# {
#   'cpu_percent': 23.4,
#   'memory_percent': 61.2,
#   'gpu_0_percent': 87.0,
#   'gpu_0_memory_percent': 52.3,
# }
```

---

## log_processor_usages

Poll `get_processor_usages()` at regular intervals and append rows to a CSV file.

```python
log_processor_usages(
    output_path: str = "resource_log.csv",
    interval_s: float = 1.0,
    duration_s: float | None = None,
) -> None
```

Runs until `duration_s` seconds elapse (or indefinitely if `None`). Writes one row per interval.

```python
import scitex as stx
import multiprocessing

# Log resource usage in the background while training
p = multiprocessing.Process(
    target=stx.resource.log_processor_usages,
    kwargs={"output_path": "training_resources.csv", "interval_s": 5.0},
)
p.start()

# ... run training ...

p.terminate()
```
