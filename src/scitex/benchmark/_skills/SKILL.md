---
name: stx.benchmark
description: Performance benchmarking, profiling, and monitoring tools for SciTeX functions.
---

# stx.benchmark

The `stx.benchmark` module provides tools for measuring, profiling, and monitoring the performance of SciTeX functions. It supports function-level benchmarking, module-level profiling, and continuous performance monitoring.

## Sub-skills

- [benchmarking.md](benchmarking.md) — `benchmark_function`, `compare_implementations`, `BenchmarkSuite`, `run_all_benchmarks`
- [profiling.md](profiling.md) — `profile_function`, `profile_block`, `profile_module`, `track_memory`
- [monitoring.md](monitoring.md) — `track_performance`, `PerformanceMonitor`, alert thresholds

## Quick Reference

```python
import scitex as stx

# Benchmark a single function
result = stx.benchmark.benchmark_function(my_func, args=(data,), iterations=50)
print(result.mean_time, result.std_time)

# Profile function calls
@stx.benchmark.profile_function
def my_func(x):
    return process(x)

report = stx.benchmark.get_profile_report()

# Monitor continuously
from scitex.benchmark.monitor import start_monitoring
start_monitoring()

@stx.benchmark.track_performance
def my_func(x):
    return process(x)

stats = stx.benchmark.get_performance_stats()

# Compare implementations
df = stx.benchmark.compare_implementations(
    {"impl_a": func_a, "impl_b": func_b},
    test_data_generator=lambda: ((data,), {})
)
```
