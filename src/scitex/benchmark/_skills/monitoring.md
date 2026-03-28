# Performance Monitoring with stx.benchmark

The monitoring sub-system provides continuous runtime tracking of functions using a global `PerformanceMonitor` instance.

## track_performance (decorator)

The `track_performance` decorator records each call's duration, memory delta, argument size, and result size into the global monitor:

```python
from scitex.benchmark import track_performance, get_performance_stats
from scitex.benchmark.monitor import start_monitoring

# Start the global monitor first
start_monitoring()

@track_performance
def load_data(path):
    return np.load(path)

# Call the function normally
for path in file_list:
    load_data(path)

# Retrieve aggregated stats
stats = get_performance_stats("load_data")
# {
#   "function": "load_data",
#   "count": N,
#   "total_time": float,
#   "avg_time": float,
#   "min_time": float,
#   "max_time": float,
#   "error_rate": float,
# }

# All functions at once
all_stats = get_performance_stats()
```

## PerformanceMonitor (direct usage)

```python
from scitex.benchmark import PerformanceMonitor

monitor = PerformanceMonitor(max_history=500)
monitor.start()

# Record metrics
from scitex.benchmark.monitor import PerformanceMetric
import time

metric = PerformanceMetric(
    timestamp=time.time(),
    function="my_operation",
    duration=0.5,
)
monitor.record_metric(metric)

# Retrieve stats
stats = monitor.get_stats("my_operation")

# Recent metrics list
recent = monitor.get_recent_metrics(n=50)

# Persist to disk and reload
monitor.save_metrics("metrics.json")
monitor.load_metrics("metrics.json")

monitor.stop()
monitor.clear()
```

## Alert Thresholds

The global monitor emits `warnings.warn()` when thresholds are exceeded. Defaults are:

| Alert type | Default threshold |
|------------|------------------|
| `slow_function` | 1.0 s |
| `memory_spike` | 100 MB |
| `error_rate` | 10% (after 10+ calls) |

```python
from scitex.benchmark.monitor import set_performance_alerts, add_performance_alert_handler

# Tighten the slow-function threshold
set_performance_alerts(slow_function=0.1)

# Custom alert callback
def my_handler(alert):
    if alert["type"] == "slow_function":
        print(f"SLOW: {alert['function']} took {alert['duration']:.2f}s")

add_performance_alert_handler(my_handler)
```

## PerformanceMetric fields

| Field | Type | Description |
|-------|------|-------------|
| `timestamp` | float | Unix time when call started |
| `function` | str | Function name |
| `duration` | float | Wall time in seconds |
| `memory_delta` | float or None | RSS change in MB (requires psutil) |
| `args_size` | int or None | `sys.getsizeof(args + kwargs)` |
| `result_size` | int or None | `sys.getsizeof(result)` |
| `exception` | str or None | Exception message if call failed |
