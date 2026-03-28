# Datetime linspace with stx.datetime

Create linearly spaced arrays of datetime objects — the temporal equivalent of `numpy.linspace`.

## linspace

```python
import datetime
from scitex.datetime import linspace

start = datetime.datetime(2023, 1, 1, 0, 0, 0)
end   = datetime.datetime(2023, 1, 1, 0, 0, 10)

# By number of samples
result = linspace(start, end, n_samples=11)
# array of 11 datetime objects from 0s to 10s, inclusive

# By sampling rate (Hz)
result = linspace(start, end, sampling_rate=100.0)
# 100 Hz * 10 seconds + 1 = 1001 samples
```

The function returns a `numpy.ndarray` of `datetime.datetime` objects.

## Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `start_dt` | `datetime.datetime` | Starting datetime (must be earlier than `end_dt`) |
| `end_dt` | `datetime.datetime` | Ending datetime |
| `n_samples` | `int` | Number of samples (mutually exclusive with `sampling_rate`) |
| `sampling_rate` | `float` | Samples per second in Hz (mutually exclusive with `n_samples`) |

## Error conditions

| Error | Condition |
|-------|-----------|
| `TypeError` | `start_dt` or `end_dt` is not a `datetime.datetime` |
| `TypeError` | `n_samples` or `sampling_rate` is not a number |
| `ValueError` | `start_dt >= end_dt` |
| `ValueError` | Both `n_samples` and `sampling_rate` provided |
| `ValueError` | Neither `n_samples` nor `sampling_rate` provided |
| `ValueError` | `sampling_rate <= 0` or `n_samples <= 0` |

## Typical Use Case

```python
import datetime
import numpy as np
from scitex.datetime import linspace

# Create 1-second time axis at 1000 Hz for EEG data
start = datetime.datetime(2024, 3, 15, 9, 0, 0)
end   = datetime.datetime(2024, 3, 15, 9, 0, 1)

time_axis = linspace(start, end, sampling_rate=1000.0)
print(len(time_axis))  # 1001
print(time_axis[0])    # 2024-03-15 09:00:00
print(time_axis[-1])   # 2024-03-15 09:00:01
```

The same function is accessible as `stx.dt.linspace(...)` via the alias module.
